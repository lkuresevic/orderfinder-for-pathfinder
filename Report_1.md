# Setting Up The Environment
All experiments were run using VPR 9.0.0, which was altered so that it loads an ordered netlist out of a .csv file, instead of sorting it by critera of descending number of sinks.

Most experiments were automated using Python scripts which can be found on [GitHub](https://github.com/lkuresevic/orderfinder-for-pathfinder/). The repository contains scripts for running VPR for packing, placement and routing, as well as reading output files and visualizing results.

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
* **congestion|max_bounding_box_size**: Sorts nets by maximum congestion in the net’s bounding box, and in case of a tie, prioritizes nets with larger bounding box sizes.
* **congestion|min_bounding_box_size**: Similar to the previous, but in case of congestion tie, prefers nets with smaller bounding boxes. 

The 10 random permutations were created by shuffling netlists retrieved from packing results. In order to account for noise from the simmulated annealing algorithm within VPR's placer, we created 5 different placements with 5 different seeds. 
Most of our metrics required for the netlist to be sorted after placement, which means that the exact orders of nets differ from placement to placement.

![Table 1](https://github.com/lkuresevic/orderfinder-for-pathfinder/blob/main/table_1.png)

While, through chance, fanouts\_size failed to dominate any of the placements and got significantly outshined at times, it was evident that no single metric or random permutation performed universaly well, or even with reliable quallity.
Although the impact netlist order has on PathFinder's QoR is undisputable, it appears to have little to do with giving priority to high fanout nets, as fanouts_size_i (the complete inverse of the current approach) outperformed fanouts_size in 3 out of 5 tests.

To further solidify this fact, we sorted the netlist by fanouts size in descending order, and then randomly shuffled the positions of the first 14 elements (the highest fanout ones). Displayed below are 5 best and 5 worst results obtained by using these slightly modified netlists.

![Table 2]()

# The Impact of A Single Swap
In order to try and identify which order alterations have the biggest impact, swapped an element in the netlist vector (sorted by fanouts_size, decreasing) with its successor and ran routing, for every net in the netlist (except the last one). We then did the same over all placements we used in the previous experiments.
We came to the following conclusions:

## The relative position of nets being swapped matters,
as demonstrated by varying effects these modifications produced across different placements, not only in quantity (how much), but also in quantiy (no effect on/improved/worsened CPD).

![A]()
![B]()
![C]()
![D]()
![E]()

We anticipated this when designing our matrics, but failed to predict in what way.

## A single swapping of two (even neighbouring) elements can significantly increase/decrease CPD 
Although all of these netlists were two inversions away from eachother (and one from the starting order) their QoR substantially differed. This highlights the fact that netlist order affects CPD through leaving PathFinder unable to use certain routing resources. Perhaps instead of looking for an approach to sort the netlist as optimally as possible, finding a way to predict which swaps imrove QoR presents a more computationally achievable goal that insists on the same insights.

We found no regularity in how relative positions, number of sinks or "conflicts" between nets affects QoR. Seeing as all considered metrics were tied to "static" features, future efforts may find more success through analyzing data collected inbetween router's iterations. 
