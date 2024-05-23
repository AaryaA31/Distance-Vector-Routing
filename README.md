[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/sJyArgKF)
# CSEE 4119 Spring 2024, Assignment 3
## Aarya Agarwal
## GitHub username: AaryaA31

*Please replace this text with information on how to run your code, description of each file in the directory, and any assumptions you have made for your code*

Running my code is as follows:
Update the variable in launch.py
Execute 'python3 launch.py' in the directory and it should take care of it self from there.

After you get the purple message from launch that DVR has started, it will take a minute for any output to appear, this is expected and seems to be the product of how the launch script handles the execution of dvr.py

I use topology to refer to the vector tables since vector tables are just a type of topology.

The files of note in the directory besides the 3 documentation ones (testing, readme, design) are topology.dat and dvr.py which serve the purposes outlined in the assignment
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
The functions of dvr.py:

'''
The next 2 functions are used by the sockets when sending and receving so that my data is sent as bytes rather than as the list of lists the vector data is held as.
This is required since sockets cannot send list items.
'''
def list_of_lists_to_string(list_of_lists):
def string_to_list_of_lists(string):


'''
This function tables in the DV arrays for the current IP address "node_topology" and "received_topology" which is a list of all the distance vectors received from the various nodes in the networks.
It then uses an implementation of Bellman_Ford based on: https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
It calls the clean topology function and log function before returning, ensuring that the returned topology is orderly and logged.
'''
def update_routing_table(node_topology, received_topology):

'''
This function is pretty straightforward, just logging the changes made to the topology to the logfile with the necessary formatting
Called by the main method as changes are made
'''
def log_topology(file, topology):

'''
Since a topology created by the Bellman-Ford method may be out of order, this function sorts it just to make it look cleaner.
Helps things be easier to read
'''
def clean_topology(node_topology):

"""
Converts an IP address string to a tuple of integers to help with sorting in the clean topology function
"""
def ip_key(ip):

'''
This function takes in the topology data once iterated and the local ip address, then creating a topology table for the current node which is then returned as a list of lists.
The topology tables are in the following format:
    <Local IP> <Node 1>:Cost:<Next Hop> ... <Node N>:Cost:<Next Hop>
'''
def get_routing_table(ip_address, topology_data):


'''
The read_topology function takes in a file path, assuming that the file is in the correct format specified for topology.dat.
After reading the file, it iterates through the lines, converting the 3rd column (the distance) into an int and storing it into a list of lists that is returned at the end.
This function also counts the number of unique IP addresses using a set and the .update() function, returning the number of nodes that exist within the network topology
'''
def read_topology(file_path):


'''
The following function is based on this stack overflow post:
https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
Describing how to access the local IP of a device. It is used to identify which node the VM is within the topology
'''
def get_local_ip():

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

One assumption I made was that no more than 5 nodes would be tested. While my methods could handle more nodes, I ran into issues with my main method.

I used this as the loop in my main method:
        for i in range(20): 

While it probably would have made more sense to use something like:
        while True:

I didn't use the while loop because when I did, the code would get stuck in the launch script and not reach my dvr.py, not even printing the print statements that come before the loop. This issue was very strange and I raised it at multiple office hours without any success solving it. I tried modifying the launch script as well and just could not figure it out. 20 iterations is enough for 5 nodes in any possible configuration but may not be enough in a case where you test 1000 nodes.

I have left the while loop in the code, commented out, feel free to go change that and you can recreate the issue I had.