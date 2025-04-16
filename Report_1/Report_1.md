# Setting Up The Environment
All experiments were conducted using VPR 9.0.0, modified to load an ordered netlist from a .csv file rather than sorting it based on the default criterion of descending sink count.

Most experiments were automated using Python scripts which can be found on [GitHub](https://github.com/lkuresevic/orderfinder-for-pathfinder/). The repository contains scripts for running VPR for packing, placement and routing, as well as reading output files and visualizing results.

Circuit and architecture - alu4.blif and k6_N10_40nm.xml

# Evaluating Netlist Sorting Criteria
Currently, netlists are sorted in descending order with regards to the number of sinks. An intuitive justification for this decision could be the assumption that routing high fanout nets first reduces routing conflcits and secures optimal critical path delay (CPD, which is the metric that we focus on in this work) for the longest spanning conenctions. However, it is known that sorting by fanout size does not provide optimal results.
In order to validate this knowledge and evaluate alternatives, we tested several alternative approaches for sorting the netlist and how they fared against random permutations.

* **fanouts_size**: Sorts nets in descending order by fanout count. Nets with more fanouts are routed first.
* **fanouts_size_i**: Sorts nets in ascending order by fanout count. Nets with fewer fanouts are routed first.
* **bounding_box_size**: Sorts nets in descending order based on the area of their bounding box (minimum rectangle enclosing source and sinks). Larger area nets are prioritized.
* **bounding_box_size_i**: Sorts nets in ascending order by bounding box area. Nets covering smaller spatial regions are routed first.
* **avg_manhattan_dist**: Sorts nets in descending order based on the average Manhattan distance between the source and each sink. 
* **avg_manhattan_dist_i**: Sorts nets in ascending order by average Manhattan distance.
* **mean_manhattan_dist**: Sorts nets in descending order based on the mean Manhattan distance between all pairs of connected CLBs (including sink-to-sink).
* **mean_manhattan_dist_i**: Sorts nets in ascending order by mean Manhattan distance.
* **connection_conflicts**: Sorts nets by the number of geometric line segment crossings with other nets. Nets with more crossings are routed first.

For the following two, a "congestion matrix" is created. It simplifies the representation of potential congestion by increasing the value of a tile/matrix element for every bounding box it is within.
* **congestion|max_bounding_box_size**: Sorts nets by maximum congestion in the net’s bounding box, and in case of a tie, prioritizes nets with larger bounding box sizes.
* **congestion|min_bounding_box_size**: Similar to the previous, but in case of congestion tie, prefers nets with smaller bounding boxes.

It is worthwhile to note the relative simplicity of most of these criteria compared to which traits they are aiming to represent.

The 10 random permutations were created by shuffling netlists retrieved from packing results. In order to account for noise from the simmulated annealing algorithm within VPR's placer, we created 5 different placements with 5 different seeds. 
Most of our metrics required for the netlist to be sorted after placement, which means that the exact orders of nets differ from placement to placement.

![Table 1](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_1.png)

While fanouts_size got significantly outshined at times, it was evident that no single metric or random permutation performed universally well, or even with reliable quality. Although the impact netlist order has on PathFinder's QoR is undisputable, it appears to have _little to do with giving priority to high fanout nets_, as fanouts_size_i (the complete inverse of the current approach) outperformed fanouts_size in 3 out of 5 tests.

To further solidify _this_ fact, we sorted the netlist by fanout size in descending order, and then randomly shuffled the positions of the first 14 elements (the highest fanout ones). Displayed below are the 5 best and 5 worst results obtained by using these slightly modified netlists.

![Table 2](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_2.png)

# The Impact of A Single Swap
In order to identify which order alterations have the greatest impact, we swapped each element in the netlist vector (originally sorted by fanouts_size in decreasing order) with its immediate successor, running routing after each swap—this was done for every net in the list except the last one. We repeated this process across all placements used in the previous experiments.
We arrived at the following conclusions:

## The relative position of nets being swapped matters...
...as demonstrated by varying effects these modifications produced across different placements, not only in quantity (how much), but also in quality (no effect on/improved/worsened CPD). We anticipated this when designing our criteria, but failed to predict in what way.

**| i | j | CPD | net_name_i | clb_i_x_y | fouts_size_i | bbox_size_i | avg_mnhttn_dist_i |** (same for net_j)

![A](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_A.png)
![B](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_B.png)
![C](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_C.png)
![D](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_D.png)
![E](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/table_E.png)
_The worse resulting CPD is relative to other permutations, the more red its tile is. Best permutations are colored white and medium results are yellow. Many of the worst/best results were achieved with some of the other ~670 net orders, not displayed here but found in the [repository](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/Report_1/)._

## A single swapping of two (even neighbouring) elements can significantly increase/decrease CPD 
Although all of these netlists were just two inversions apart from each other (and one from the starting order), their QoR varied substantially. As a result, no sorting criterion which remotely simplifies the netlists' and RR graphs' representation can be relied upon, as minimal inaccuracies annul potential benefits of ordering the netlist precisely according to some yet be defined rule.

Perhaps a framework could be designed to predict which individual swap improves QoR the most (it remains unclear how).

We found no consistent pattern in how relative positions, number of sinks, or “conflicts” between nets influence QoR. Reordering pairs of seemingly unrelated nodes (far apart and non-overlapping bounding boxes) on occasion resulted in big variations to CPD, suggesting difficult to predict knock-on effects. Since all considered metrics were tied to "static" features, future efforts may find more success through analyzing data collected inbetween router's iterations. 
