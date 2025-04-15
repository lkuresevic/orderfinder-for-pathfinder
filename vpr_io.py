import csv
import os
import xml.etree.ElementTree as ET

def read_placement(place_file):
    # Create a dictionary that maps a block to its coordinates
    placement = {}
    with open(place_file, 'r') as dot_place:
        for _ in range(5):
            next(dot_place)
        for line in dot_place:
            block = line.split()
            placement[block[0]] = [block[1], block[2]]
    return placement

def read_netlist(net_file):
    def map_subcomponent_to_clb(block, clb_name, subcomponent_to_clb):
        for subcomponent in block:
            if 'name' in subcomponent.attrib:
                subcomponent_to_clb[subcomponent.attrib['name']] = clb_name
                map_subcomponent_to_clb(subcomponent, clb_name, subcomponent_to_clb)

    nets = {}
    subcomponent_to_clb = {}
    tree = ET.parse(net_file)
    root = tree.getroot()
    
    # Iterate over all CLB's in the netlist
    for block in root:
        if 'name' in block.attrib:
            # Compile a list of all nets in the netlist
            inputs = block[0][0].text.split(' ')
            for pin in inputs:
                if pin != 'open':
                   if pin in nets.keys():
                        nets[pin].append(block.attrib['name'])
                   else:
                        nets[pin] = [block.attrib['name']]
            
            # Map all clusters/modes/primitives to their CLB's, for the purpose of locating them in the placement
            
            map_subcomponent_to_clb(block, block.attrib['name'], subcomponent_to_clb)    
    return nets, subcomponent_to_clb

def read_log_file():
    with open("./vpr_stdout.log", "r") as log_file:
        line = next(log_file)
        while line[0:40] != "Final critical path delay (least slack):":
            line = next(log_file)
        line_list = line.split(" ")
        return line_list[6]

def read_seeds_file(seeds_file):
    seeds_list = []
    with open(seeds_file, "r") as seeds_txt:
        for seed in seeds_txt:
            seeds_list.append(seed[:-1])

    return seeds_list

def store_routing_results(results_file, results_list):
    with open(results_file, "w", newline="") as results_txt:
        permutation_id = 1
        for result in results_list:
            results_txt.write(str(permutation_id)+": "+str(result)+"\n")
            permutation_id += 1

def store_seeds(seeds_list, seeds_file):
    with open(seeds_file, "w", newline="") as seeds_txt:
        for seed in seeds_list:
            seeds_txt.write(str(seed)+"\n")

def create_netlist_csv(csv_file, nets, subcomponent_to_clb, placement):
    # Calculate bounding box size (width and height)
    def calculate_bounding_box_size(source_coordinates, sink_coordinates_list):
        # List of all coordinates
        sink_coordinates_list.append(source_coordinates)

        x_coordinates = [int(coordinate[0]) for coordinate in sink_coordinates_list]
        y_coordinates = [int(coordinate[1]) for coordinate in sink_coordinates_list]
            
        width = max(x_coordinates) - min(x_coordinates) + 1
        height = max(y_coordinates) - min(y_coordinates) + 1
        return width*height

    # Calculate Manhattan distance between source and each sink
    def calculate_manhattan_distance(source_coordinates, sink_coordinates_list):
        distances = []
        for sink_coordinates in sink_coordinates_list:
            dist = abs(int(source_coordinates[0]) - int(sink_coordinates[0])) + abs(int(source_coordinates[1]) - int(sink_coordinates[1]))
            distances.append(dist)
        return distances


    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ['net_name', 'source_clb', 'sink_clbs', 'fanouts_size', 'bounding_box_size', 'avg_manhattan_dist', 'mean_manhattan_dist']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for net_name in nets.keys():
            # Get the source CLB
            source_clb = subcomponent_to_clb[net_name]
            # Get coordinates of the source CLB
            source_coordinates = placement[source_clb]
            # Get coordinates of all sink CLBs
            sink_clbs = nets[net_name]
            sink_coordinates_list = [placement[sink] for sink in sink_clbs]

            # Calculate metrics
            fanouts_size = len(sink_clbs)
            bounding_box_size = calculate_bounding_box_size(source_coordinates, sink_coordinates_list)
            manhattan_distances = calculate_manhattan_distance(source_coordinates, sink_coordinates_list)
            avg_manhattan_dist = sum(manhattan_distances) / (len(manhattan_distances) - 1) if manhattan_distances else 0
            mean_manhattan_dist = sorted(manhattan_distances)[len(manhattan_distances)//2] if manhattan_distances else 0

            # Write to CSV
            writer.writerow({
                'net_name': net_name,
                'source_clb': source_clb,
                'sink_clbs': sink_clbs,
                'fanouts_size': fanouts_size,
                'bounding_box_size': bounding_box_size,
                'avg_manhattan_dist': avg_manhattan_dist,
                'mean_manhattan_dist': mean_manhattan_dist
            })

    return


def delete_excess_files(circuit_name):
    if os.path.exists("./"+circuit_name+".place"):
        os.remove("./"+circuit_name+".place")
    if os.path.exists("./"+circuit_name+".route"):
        os.remove("./"+circuit_name+".route")
    if os.path.exists("./"+circuit_name+".net"):
        os.remove("./"+circuit_name+".net")
    if os.path.exists("./"+circuit_name+".net.post_routing"):
        os.remove("./"+circuit_name+".net.post_routing")
    if os.path.exists("./current_permutation.csv"):
        os.remove("./current_permutation.csv")
    if os.path.exists("./packing_pin_util.rpt"):
        os.remove("./packing_pin_util.rpt")
    if os.path.exists("./pre_pack.report_timing.setup.rpt"):
        os.remove("./pre_pack.report_timing.setup.rpt")
    if os.path.exists("./report_timing.hold.rpt"):
        os.remove("./report_timing.hold.rpt")
    if os.path.exists("./report_timing.setup.rpt"):
        os.remove("./report_timing.setup.rpt")    
    if os.path.exists("./report_unconstrained_timing.hold.rpt"):
        os.remove("./report_unconstrained_timing.hold.rpt")
    if os.path.exists("./report_unconstrained_timing.setup.rpt"):
        os.remove("./report_unconstrained_timing.setup.rpt")
    if os.path.exists("./vpr_stdout.log"):
        os.remove("./vpr_stdout.log")
