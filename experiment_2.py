import os
import random
from utils import *

current_permutation_csv = os.path.join(".", "current_permutation.csv")

def experiment_2(vpr_path, xml_file, blif_file, dest_folder, seed):
    # Read packing
    net_file = os.path.join(".", dest_folder, dest_folder + ".net")
    nets, subcomponent_to_clb = read_netlist(net_file)

    # Set subfolder
    subfolder = os.path.join(".", dest_folder, dest_folder + "-" + seed)
    
    # Read placement            
    place_file = os.path.join(subfolder, dest_folder + "-" + seed + ".place")
    placement = read_placement(place_file)

    # Read .csv file
    csv_file = os.path.join(subfolder, dest_folder + "-" + seed + ".csv") 
    df = pd.read_csv(csv_file)

    loaded_permutation = sort_list_by_criteria(df, "fanouts_size", placement)
    current_permutation = []
    with open(os.path.join(subfolder, dest_folder + "-" + seed + "-swap_results.csv"), "w", newline="") as swap_results:
        store_res = csv.writer(swap_results)
        for i in range(1, len(loaded_permutation)):
            current_permutation = loaded_permutation.copy()
            current_permutation[i], current_permutation[i-1] = current_permutation[i-1], current_permutation[i]

            # Set current permutation
            with open(current_permutation_csv, "w", newline="") as current_permutation_file:
               set_permutation = csv.writer(current_permutation_file)
               set_permutation.writerow(current_permutation)
            route_file = place_file[:-6]+"-"+str(i-1) + "-" + str(i)+".route"
            generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file)
            a = current_permutation[i-1]
            b = current_permutation[i]
            store_res.writerow([str(i-1), str(i), read_log_file(),
            a, placement[subcomponent_to_clb[a]], 
            df.loc[df['net_name'] == a, 'fanouts_size'].values[0], 
            df.loc[df['net_name'] == a, 'bounding_box_size'].values[0], 
            df.loc[df['net_name'] == a, 'avg_manhattan_dist'].values[0], 
            b, placement[subcomponent_to_clb[b]], 
            df.loc[df['net_name'] == b, 'fanouts_size'].values[0], 
            df.loc[df['net_name'] == b, 'bounding_box_size'].values[0], 
            df.loc[df['net_name'] == b, 'avg_manhattan_dist'].values[0]])

        for i in range(30):
            i = random.randint(1, len(loaded_permutation)-1)
            if i % 2 == 0:
                j = random.randint(1, i-1)
            else:
                j = random.randint(i+1, len(loaded_permutation)-1)

            current_permutation = loaded_permutation.copy()
            current_permutation[i], current_permutation[j] = current_permutation[j], current_permutation[i]
            # Set current permutation
            with open(current_permutation_csv, "w", newline="") as current_permutation_file:
                set_permutation = csv.writer(current_permutation_file)
                set_permutation.writerow(current_permutation)
            route_file = place_file[:-6]+"-"+str(j) + "-" + str(i)+".route"
            generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file)
            
            a = current_permutation[j]
            b = current_permutation[i]
            store_res.writerow([str(j), str(i), read_log_file(), 
a, placement[subcomponent_to_clb[a]], 
df.loc[df['net_name'] == a, 'fanouts_size'].values[0], 
df.loc[df['net_name'] == a, 'bounding_box_size'].values[0], 
df.loc[df['net_name'] == a, 'avg_manhattan_dist'].values[0], 
b, placement[subcomponent_to_clb[b]], 
df.loc[df['net_name'] == b, 'fanouts_size'].values[0], 
df.loc[df['net_name'] == b, 'bounding_box_size'].values[0], 
df.loc[df['net_name'] == b, 'avg_manhattan_dist'].values[0]])
