import glob
import sys
import random

from utils import *

current_permutation_csv = os.path.join(".", "current_permutation.csv")

def generate_n_placements(vpr_path, xml_file, blif_file, dest_folder, n):
    # Generate packing
    net_file = os.path.join(".", dest_folder, dest_folder + ".net")
    generate_packing(vpr_path, xml_file, blif_file, dest_folder, net_file)
    nets, subcomponent_to_clb = read_netlist(net_file)
    
    seeds = []
    # Generate five random placement seeds to account for noise in the simmulated annealing algorithm  
    for i in range(n):
        # Generate seed
        if i == 0:
            seed = 1
        else:
            seed = random.randrange(0, 2147483647)
        seeds.append(seed)

        print("--------------------------------------------------------")
        print("Generating placement and routing for seed: " + str(seed))
        print("--------------------------------------------------------")

        # Create subfolder 
        subfolder = os.path.join("./", dest_folder, dest_folder + "-" + str(seed))
        os.makedirs(subfolder, exist_ok=True)

        # Generate placement            
        place_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".place")
        generate_placement(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, seed)
        placement = read_placement(place_file)
        
        # Generate .csv file
        csv_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".csv")
        create_netlist_csv(csv_file, nets, subcomponent_to_clb, placement)
            
    # Store all seeds used for placement generation
    store_seeds(seeds, os.path.join(".", dest_folder, dest_folder + "-seeds.txt"))

def generate_routings_for_set_placements(vpr_path, xml_file, blif_file, dest_folder, seeds, sorting_criteria, n):
    net_file = os.path.join(".", dest_folder, dest_folder + ".net")
    nets, subcomponent_to_clb = read_netlist(net_file)
  
    # Generate 4 predetermined and 246 random permutations of nets in the netlist
    netlist_permutations_csv = os.path.join(".", dest_folder, dest_folder + "-permutations" + ".csv")
    with open(netlist_permutations_csv, "w", newline="") as permutations_file:
        writer = csv.writer(permutations_file)        
        for _ in range(n):
            permutation = list(nets.keys())
            random.shuffle(permutation)
            writer.writerow(permutation)
    
    for seed in seeds:
        subfolder = os.path.join("./", dest_folder, dest_folder + "-" + str(seed))
        place_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".place")
        placement = read_placement(place_file)            
        
        csv_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".csv")
        # Generate routings for all chosen netlist permutations
        with open(netlist_permutations_csv, "r") as permutations_file:
            reader = csv.reader(permutations_file)
            results = []
            permutation_id = 1

            results = []
            permutation_id = 1

            # Sort by criteria
            df = pd.read_csv(csv_file)
            
            for criteria in sorting_criteria:
                with open(current_permutation_csv, "w", newline="") as current_permutation_file:
                        set_permutation = csv.writer(current_permutation_file)
                        set_permutation.writerow(sort_list_by_criteria(df, criteria, placement))
                route_file = place_file[:-6]+"-"+str(permutation_id)+".route"
                generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file)
                results.append(read_log_file())
                permutation_id += 1
            
            # Iterate over random permutations
            for permutation in reader:
                # Run VPR for routing
                netlist_permutation = [item for item in permutation]
                with open(current_permutation_csv, "w", newline="") as current_permutation_file:
                    set_permutation = csv.writer(current_permutation_file)
                    set_permutation.writerow(netlist_permutation)
                route_file = place_file[:-6]+"-"+str(permutation_id)+".route"
                generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file)
                results.append(read_log_file())
                permutation_id += 1

            # Store routing results for each permutation
            results_file = os.path.join(".", subfolder, "results-of-" + dest_folder + "-" + str(seed) + "-permutations" + ".txt")
            store_routing_results(results_file, results)

def print_permutation(vpr_path, xml_file, blif_file, dest_folder, seed, sorting_criteria):
    net_file = os.path.join(".", dest_folder, dest_folder + ".net")
    nets, subcomponent_to_clb = read_netlist(net_file)

    subfolder = os.path.join("./", dest_folder, dest_folder + "-" + str(seed))
    place_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".place")
    placement = read_placement(place_file)            
    
    csv_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".csv")
    output_csv = os.path.join(".", subfolder, dest_folder + "-criteria.csv")
    # Sort by criteria
    df = pd.read_csv(csv_file)
    with open(output_csv, "w", newline="") as output_file:
        set_permutation = csv.writer(output_file)
        for criteria in sorting_criteria:
            set_permutation.writerow(sort_list_by_criteria(df, criteria, placement))
  

def experiment_1(vpr_path, xml_file, blif_file, dest_folder):
    generate_n_placements(vpr_path, xml_file, blif_file, dest_folder, 5)
            
    sorting_criteria = ['fanouts_size', 'bounding_box_size', 'avg_manhattan_dist', 'mean_manhattan_dist', 'fanouts_size_i', 'bounding_box_size_i', 'avg_manhattan_dist_i', 'mean_manhattan_dist_i', 'connection_conflicts', 'congestion|max_bounding_box_size', 'congestion|min_bounding_box_size']
    
    seeds_file = os.path.join(".", dest_folder, dest_folder + "-seeds.txt")
    seeds = read_seeds_file(seeds_file)
    
    generate_routings_for_set_placements(vpr_path, xml_file, blif_file, dest_folder, seeds, sorting_criteria, 10)
    
    delete_excess_files(xml_file[:-5])
