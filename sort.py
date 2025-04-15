import pandas as pd
from shapely.geometry import LineString

import numpy as np

def sort_list_by_criteria(df, criteria, placement):
    if criteria in ['fanouts_size', 'bounding_box_size', 'avg_manhattan_dist', 'mean_manhattan_dist']:
        ordered_list = df.sort_values(by=criteria, ascending=False)['net_name'].tolist()
        return ordered_list
    elif criteria in ['fanouts_size_i', 'bounding_box_size_i', 'avg_manhattan_dist_i', 'mean_manhattan_dist_i']:
        ordered_list = df.sort_values(by=criteria[:-2], ascending=True)['net_name'].tolist()
        return ordered_list

    if criteria == 'connection_conflicts':
        ordered_list = sort_list_by_connection_conflicts(df, placement)
        return ordered_list
    elif criteria == 'congestion|max_bounding_box_size':
        ordered_list = sort_list_by_congestion(df, placement, 'max_bounding_box_size')
        return ordered_list
    elif criteria == 'congestion|min_bounding_box_size':
        ordered_list = sort_list_by_congestion(df, placement, 'min_bounding_box_size')
        return ordered_list

def sort_list_by_connection_conflicts(df, placement):
    def get_coord(clb_name):
        if clb_name not in placement:
            return None
        x, y = placement[clb_name]
        return (float(x), float(y))

    def get_net_lines(row):
        src = get_coord(row['source_clb'])
        sinks = row['sink_clbs']
        lines = []
        if not isinstance(sinks, list):
            return lines
        for sink in sinks:
            sink_coord = get_coord(sink)
            if src and sink_coord:
                lines.append(LineString([src, sink_coord]))
        return lines

    # Preprocess: Convert stringified sink_clbs to lists
    df = df.copy()
    df['sink_clbs'] = df['sink_clbs'].apply(eval)  # Caution: use ast.literal_eval for untrusted data

    # Build dictionary of net_name -> list of LineString connections
    net_lines = {}
    for _, row in df.iterrows():
        lines = get_net_lines(row)
        if lines:
            net_lines[row['net_name']] = lines

    # Count geometric crossings
    conflict_counts = {net: 0 for net in net_lines}
    net_names = list(net_lines.keys())

    for i in range(len(net_names)):
        net_i = net_names[i]
        for j in range(i+1, len(net_names)):
            net_j = net_names[j]
            for line1 in net_lines[net_i]:
                for line2 in net_lines[net_j]:
                    if line1.crosses(line2):
                        conflict_counts[net_i] += 1
                        conflict_counts[net_j] += 1

    # Sort nets by descending number of conflicts
    sorted_nets = sorted(conflict_counts, key=lambda net: conflict_counts[net], reverse=True)

    return sorted_nets


def sort_list_by_congestion(df, placement, suffix):
    # Convert placement coordinates to integers
    int_placement = {clb: (int(float(x)), int(float(y))) for clb, (x, y) in placement.items()}

    # Determine matrix size (min is 0, max is from placement)
    max_x = max(coord[0] for coord in int_placement.values())
    max_y = max(coord[1] for coord in int_placement.values())
    congestion_matrix = np.zeros((max_x + 1, max_y + 1), dtype=int)

    # Preprocess sink_clbs
    df = df.copy()
    df['sink_clbs'] = df['sink_clbs'].apply(eval)  # Use literal_eval for safety in production

    # Populate congestion matrix
    for _, row in df.iterrows():
        clbs = [row['source_clb']] + row['sink_clbs']
        coords = [int_placement[clb] for clb in clbs if clb in int_placement]
        if not coords:
            continue
        xs, ys = zip(*coords)
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                congestion_matrix[x][y] += 1

    # Compute congestion for each net
    net_congestion = {}
    for _, row in df.iterrows():
        clbs = [row['source_clb']] + row['sink_clbs']
        coords = [int_placement[clb] for clb in clbs if clb in int_placement]
        if not coords:
            continue
        xs, ys = zip(*coords)
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        max_tile_congestion = max(congestion_matrix[x][y] for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1))
        net_congestion[row['net_name']] = {
            'max_congestion': max_tile_congestion,
            'bounding_box_size': row['bounding_box_size']
        }

    # Sort based on criteria
    def sort_key(item):
        net, info = item
        primary = info['max_congestion']
        secondary = info['bounding_box_size']
        if suffix == 'max_bounding_box_size':
            secondary = -secondary  # descending
        return (primary, secondary)

    sorted_nets = sorted(net_congestion.items(), key=sort_key, reverse=True)
    return [net for net, _ in sorted_nets]
