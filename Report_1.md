# Setting Up The Environment
All experiments were run using VPR 9.0.0, which was altered so that it loads an ordered netlist out of a .csv file, instead of sorting it by critera of descending number of sinks.

Most experiments were automated using Python scripts which can be found on [GitHub](https://github.com/lkuresevic/orderfinder-for-pathfinder/). The repository contains scripts for running VPR for packing, placement and routing, as well as reading output files and visualizing results.

# Comparing Netlist Sorting Criteria
Currently, netlists are sorted in descending order with regards to the number of sinks. 
