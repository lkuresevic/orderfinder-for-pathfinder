import os
import pandas as pd

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import networkx as nx

def create_results_dict(criteria, subfolder):
    # create dictionary: {num_inversions : [CPD]}
    results_dict = {}
    id_to_num_inv = {}
   

    with open(subfolder+subfolder[2:-1]+"-seeds.txt", "r") as seeds:
        seed_id = 0
        for seed in seeds:
            csv_file = os.path.join(subfolder+subfolder[2:-1] + "-"+str(seed)[:-1]+ "/" + subfolder[2:-1] + "-"+str(seed)[:-1] + ".csv")
            df = pd.read_csv(csv_file)

            place_file = os.path.join(subfolder+subfolder[2:-1] + "-"+str(seed)[:-1]+ "/" + subfolder[2:-1] + "-"+str(seed)[:-1] + ".place")

            ordered_list = sort_list_by_criteria(df, criteria, place_file)

            with open(subfolder[:-1]+ subfolder[1:-1] + "-permutations.csv") as permutations_file:
                # count the num_inversions and create dictionary {id_perm : num_inv}
                permutation_id = 1
                
                # Sort the list
                
                # Sort nets by fanouts size
                netlist_order = df.sort_values(by='fanouts_size', ascending=False)['net_name'].tolist()
                num_inversions = count_num_inv(netlist_order, ordered_list) ### code
                if permutation_id in id_to_num_inv.keys():
                    id_to_num_inv[permutation_id].append(num_inversions)
                else:
                    id_to_num_inv[permutation_id] = [num_inversions]
                permutation_id += 1

                # Sort nets by bounding box size
                netlist_order = df.sort_values(by='bounding_box_size', ascending=False)['net_name'].tolist()
                num_inversions = count_num_inv(netlist_order, ordered_list) ### code
                if permutation_id in id_to_num_inv.keys():
                    id_to_num_inv[permutation_id].append(num_inversions)
                else:
                    id_to_num_inv[permutation_id] = [num_inversions]
                permutation_id += 1

                # Sort nets by average manhattan distance
                netlist_order = df.sort_values(by='avg_manhattan_dist', ascending=False)['net_name'].tolist()
                num_inversions = count_num_inv(netlist_order, ordered_list) ### code
                if permutation_id in id_to_num_inv.keys():
                    id_to_num_inv[permutation_id].append(num_inversions)
                else:
                    id_to_num_inv[permutation_id] = [num_inversions]
                permutation_id += 1


                # Sort nets by mean manhattan distance
                netlist_order = df.sort_values(by='mean_manhattan_dist', ascending=False)['net_name'].tolist()
                num_inversions = count_num_inv(netlist_order, ordered_list) ### code
                if permutation_id in id_to_num_inv.keys():
                    id_to_num_inv[permutation_id].append(num_inversions)
                else:
                    id_to_num_inv[permutation_id] = [num_inversions]
                permutation_id += 1
                
                for permutation in permutations_file:
                    netlist_order = permutation.split(",")
                    netlist_order[-1] = (netlist_order[-1])[:-1]
                    num_inversions = count_num_inv(netlist_order, ordered_list) ### code
                    if permutation_id in id_to_num_inv.keys():
                        id_to_num_inv[permutation_id].append(num_inversions)
                    else:
                        id_to_num_inv[permutation_id] = [num_inversions]
                        
                    permutation_id += 1
            txt_file = subfolder[:-1] + subfolder[1:-1] + "-" + str(seed)[:-1] + "/results-of-" + subfolder[2:-1] + "-" + str(seed)[:-1] + "-permutations.txt"
            with open(txt_file, "r") as result:
                permutation_id = 1
                for line in result:
                    cpd = (line.split(" ")[1])[:-1]
                    num_inv = (id_to_num_inv[permutation_id])[seed_id]
                    if num_inv not in results_dict.keys():
                        results_dict[num_inv] = []
                        results_dict[num_inv].append(cpd)
                    else:
                        results_dict[num_inv].append(cpd)
                    permutation_id += 1
            seed_id += 1
    return results_dict, id_to_num_inv

def plot_inversions_over_cpd(subfolder, criteria):
    
    results_dict, _ = create_results_dict(criteria, subfolder)

    x_vals = []
    y_vals = []
    
    for num_inv, delays in results_dict.items():
        for delay in delays:
            x_vals.append(float(delay))
            y_vals.append(num_inv)
    
    # Create plot
    plt.figure(figsize=(12, 8))
    plt.scatter(x_vals, y_vals, color='blue', alpha=0.6, s=10)
    
    # Formatting
    plt.title('Inversions by ' + criteria + ' over Critical Path Delay')
    plt.xlabel('Critical Path Delay (ns)')
    plt.ylabel('Number of Inversions')
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Adjust y-axis to handle large inversion counts
    plt.ticklabel_format(style='plain', axis='y')
    
    # Adjust x-axis limits to focus on relevant range
    plt.xlim(min(x_vals)*0.95, max(x_vals)*1.05)
    
    plt.show()

def plot_placement(placement, nets, subcomponent_to_clb):
    # 
    # Note: DeepSeek Generated
    #
    yellow = '[7190]'
    blue = '[7202]'
    red = '[649]'
    special_nets = {yellow, blue, red}
    
    special_nodes = set()
    net_membership = {}
    
    for source in nets.keys():
        is_special = False
        if source in special_nets:
            is_special = True
            special_nodes.add(source)
            if source not in net_membership:
                net_membership[source] = set()
            net_membership[source].add(source)
        
        for sink in nets[source]:
            if sink in special_nets or is_special:
                special_nodes.add(sink)
                if sink not in net_membership:
                    net_membership[sink] = set()
                if source in special_nets:
                    net_membership[sink].add(source)
                if is_special:
                    net_membership[sink].add(source)
    
    edges = []
    nodes = {}
    
    for source in nets.keys():
        # Only process if source or any of its sinks are in our special nets
        if source in special_nets or any(sink in special_nets for sink in nets[source]):
            if source not in nodes:
                nodes[source] = placement[subcomponent_to_clb[source]]
            for sink in nets[source]:
                if sink in special_nets or source in special_nets:
                    edges.append((source, sink))
                    if sink not in nodes:
                        nodes[sink] = placement[subcomponent_to_clb[sink]]

    # Create graph
    G = nx.DiGraph()
    G.add_nodes_from(nodes.keys())
    G.add_edges_from(edges)
    pos = {node: (float(x), float(y)) for node, (x, y) in nodes.items()}

    # Define color mapping based on net membership
    def get_node_color(node):
        nets = net_membership.get(node, set())
        
        if {yellow, blue, red}.issubset(nets):
            return 'black'  # all three - shouldn't happen based on your spec
        
        if {yellow, blue}.issubset(nets):
            return 'green'
        elif {blue, red}.issubset(nets):
            return 'purple'
        elif {yellow, red}.issubset(nets):
            return 'orange'
        elif yellow in nets:
            return 'yellow'
        elif blue in nets:
            return 'blue'
        elif red in nets:
            return 'red'
        else:
            return 'black'

    # Get node colors
    node_colors = [get_node_color(node) for node in G.nodes()]
    
    # Get edge colors (color of the source node)
    edge_colors = []
    for edge in G.edges():
        source = edge[0]
        edge_colors.append(get_node_color(source))

    # Create labels - only show for our special nets
    labels = {node: node if node in special_nets else '' for node in G.nodes()}

    # Draw the graph
    plt.figure(figsize=(10, 8))

    # Draw nodes with their assigned colors
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=500,
        node_color=node_colors,
    )

    # Draw edges with their assigned colors
    nx.draw_networkx_edges(
        G,
        pos,
        edge_color=edge_colors,
        arrows=True,
        arrowstyle='->',
        arrowsize=15,
    )

    # Draw labels (only for our special nets)
    nx.draw_networkx_labels(
        G,
        pos,
        labels=labels,
        font_size=10,
        font_weight='bold', 
    )

    plt.title("")
    plt.grid(True)
    plt.show()

