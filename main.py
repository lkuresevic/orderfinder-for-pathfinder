import glob
import os

from utils import *
from experiment_1 import *
from experiment_2 import *
from experiment_3 import *

current_permutation_csv = os.path.join(".", "current_permutation.csv")


def route_over_seed(vpr_path, xml_file, blif_file, dest_folder, seed):
    net_file = os.path.join(".", dest_folder, dest_folder + ".net")
    subfolder = os.path.join("./", dest_folder, dest_folder + "-" + str(seed))
    place_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".place")
    placement = read_placement(place_file)            
    
    csv_file = os.path.join(".", subfolder, dest_folder + "-" + str(seed) + ".csv")

    route_file = place_file[:-6]+"-"+"test.route"
    generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file)

if __name__ == "__main__": 
    xml_files = glob.glob(os.path.join('./', '*.xml'))
    blif_files = glob.glob(os.path.join('./', '*.blif'))
    
    vpr_path = "../build/vpr/vpr"
    
    # Iterate over architectures
    for xml_file in xml_files:
        # Iterate over circuits
        for blif_file in blif_files:
            # Create destination folder
            dest_folder = xml_file[2:-4]+"-"+blif_file[2:-5]  
            os.makedirs("./"+dest_folder, exist_ok=True)
      
            seeds_file = os.path.join(".", dest_folder, dest_folder + "-seeds.txt")
            seeds = read_seeds_file(seeds_file)
            for seed in seeds:
                experiment_2(vpr_path, xml_file, blif_file, dest_folder, seed)

            delete_excess_files(blif_file[2:-5])
            
