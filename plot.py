def plot_placement(placement, nets, subcomponent_to_clb):
    # Define the special nets we care about
    yellow = '[7190]'
    blue = '[7202]'
    red = '[649]'
    special_nets = {yellow, blue, red}
    
    # First, find all nodes that belong to our special nets (either as sources or sinks)
    special_nodes = set()
    net_membership = {}  # To track which special nets each node belongs to
    
    for source in nets.keys():
        # Check if this source is one of our special nets or connected to them
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
    
    # Now create edges only for connections involving our special nets
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
