# The effect of netlist order on QoR of PathFinder
The order in which PathFinder routes nets significantly effects the QoR in terms of critical path delay, as identified by [Rubin and DeHon](https://ic.ese.upenn.edu/pdf/pathfinder_noise_fpga2011.pdf).

This project attempts to understand how different orderings of nets affect the QoR, and aims to provide an alternative approach to sorting the netlist.

# VPR's implementation of PathFinder
All experiments are pefromed using VPR version 9.0.0.

With the goal of evaluating different netlist orders, SerialNetlistRouter.tpp was modified.

Instead of sortin by fanout size
```cpp
  /* Sort so net with most sinks is routed first */
  auto sorted_nets = std::vector<ParentNetId>(_net_list.nets().begin(), _net_list.nets().end());
  std::stable_sort(sorted_nets.begin(), sorted_nets.end(), [&](ParentNetId id1, ParentNetId id2) -> bool {
      return _net_list.net_sinks(id1).size() > _net_list.net_sinks(id2).size();
  });
```
VPR loads netlist permutations from a .csv file updated either manually or by a Python script:
```cpp
  std::string csv_filename = "path/to/order_file.csv";
  std::ifstream file(csv_filename);

  if (!file.is_open()) {
      std::cerr << "Error: Could not open file " << csv_filename << std::endl;
      /* Sort so net with most sinks is routed first */   
      std::stable_sort(sorted_nets.begin(), sorted_nets.end(), [&](ParentNetId id1, ParentNetId id2) -> bool {
          return _net_list.net_sinks(id1).size() > _net_list.net_sinks(id2).size();
      });
  }
  else {
      /* Read net names from CSV in order */
      std::vector<std::string> csv_net_names;
      std::string line;
      while (std::getline(file, line)) {
          std::stringstream ss(line);
          std::string net_name;
          while (std::getline(ss, net_name, ',')) {
              if (!net_name.empty()) {
                  csv_net_names.push_back(net_name);
              }
          }
      }

      /* Create a mapping from net name to its desired position */
      std::unordered_map<std::string, size_t> net_name_to_order;
      for (size_t i = 0; i < csv_net_names.size(); ++i) {
          net_name_to_order[csv_net_names[i]] = i;
      }

      /* Sort sorted_nets based on CSV order */
      std::stable_sort(sorted_nets.begin(), sorted_nets.end(), 
          [&](ParentNetId id1, ParentNetId id2) {
              /* Get net names */
              std::string name1 = _net_list.net_name(id1);
              std::string name2 = _net_list.net_name(id2);
              
              /* Find their positions in CSV */
              auto it1 = net_name_to_order.find(name1);
              auto it2 = net_name_to_order.find(name2);
              
              size_t pos1 = (it1 != net_name_to_order.end()) ? it1->second : csv_net_names.size();
              size_t pos2 = (it2 != net_name_to_order.end()) ? it2->second : csv_net_names.size();
              
              return pos1 < pos2;
          }
      );
  }
```
