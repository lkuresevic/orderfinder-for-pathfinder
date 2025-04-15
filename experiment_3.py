import os
import random
from utils import *

current_permutation_csv = os.path.join(".", "current_permutation.csv")

def experiment_3(vpr_path, xml_file, blif_file, dest_folder, seed):
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

    loaded_permutation = sort_list_by_criteria(df, criteria, placement)
    current_permutation = []
    with open(os.path.join(subfolder, dest_folder + "-" + seed + "-permute_start_results.csv"), "w", newline="") as swap_results:
        store_res = csv.writer(swap_results)
        for i in range(1, 100):
            head = loaded_permutation[:14].copy()
            tail = loaded_permutation[14:].copy()
            
            random.shuffle(head)

            current_permutation = head + tail

            # Set current permutation
            with open(current_permutation_csv, "w", newline="") as current_permutation_file:
               set_permutation = csv.writer(current_permutation_file)
               set_permutation.writerow(current_permutation)
            route_file = place_file[:-6]+"-" + str(i)+"-head.route"
            generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file)
            a = current_permutation[i]
            b = current_permutation[i-1]
            store_res.writerow([read_log_file(), 
current_permutation[0],
current_permutation[1],
current_permutation[2],
current_permutation[3],
current_permutation[4],
current_permutation[5],
current_permutation[6],
current_permutation[7],
current_permutation[8],
current_permutation[9],
current_permutation[10],
current_permutation[11],
current_permutation[12],
current_permutation[13],
current_permutation[14]])
