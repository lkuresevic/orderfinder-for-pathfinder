import subprocess

from utils import *
   
def run_command_in_terminal(command, directory):
    try:
        result = subprocess.run(command, cwd=directory, check=True, text=True, capture_output=True)
        print("Command output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(command)


def generate_packing(vpr_path, xml_file, blif_file, dest_folder, net_file):
    run_command_in_terminal([vpr_path, xml_file, blif_file, "--pack",
                                    "--net_file", net_file], 
                                    "./")

def generate_placement(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, seed):
    run_command_in_terminal([
            vpr_path, xml_file, blif_file,
            "--seed", str(seed),        
            "--place",                  
            "--net_file", net_file,
            "--place_file", place_file], "./")

def generate_routing(vpr_path, xml_file, blif_file, dest_folder, net_file, place_file, route_file):
    run_command_in_terminal([vpr_path, xml_file, blif_file, "--route", 
                            "--net_file", net_file,
                            "--place_file", place_file,
                            "--route_file", route_file],
                            "./")
