#
# Columbia University - CSEE 4119 Computer Network
# Assignment 3 - Distance Vector Routing
#
# dvr.py - the Distance Vector Routing (DVR) program announces its routing table to its neighbors and
# updates its routing table based on the received routing tables from its neighbors
#

# we provide an overlay program for you to test your DVR program
# 1. configure the topology.dat file to set up the network topology.
#    each line contains two nodes and their cost, separated by a space.
#    please use the internal IP of each Google cloud VM.
#    make sure all VMs use the same topology file.
#
# 2. run the overlay with "./overlay <overlay_port> <internal_port> <topology_file>"
#
# 3. wait until the overlay has finished setting up. you will see the following phrase:
#    "waiting for connection from the network process..."
#    then. you will connect to the overlay in the local machine
# through the overlay port (default 60000)
#
# 4. parse the topology.dat file to retrieve the total number of
# nodes in the network and your neighbors with the corresponding cost
#
# 5. any message sent to the overlay will be broadcasted to the neighbors only
#    - design a protocol for sending and receiving a routing table
#    - keep announcing the table to the neighbors
#    - update your own table based on the received routing tables
#
# 6. log the routing table at the initial state, and whenever it is updated
#    using the following format
#    <neighbor_1>:<cost_1>:<next_hop_1> ... <neighbor_n>:<cost_n>:<next_hop_n>
#    and save the log file to log_<internal_ip>.txt.
#
#    e.g., for log_10.128.0.2.txt
#    <10.128.0.3>:7:<10.128.0.3> <10.128.0.4>:2:<10.128.0.4>
#    <10.128.0.3>:5:<10.128.0.4> <10.128.0.4>:2:<10.128.0.4>
#

import socket
import sys
import threading
import time
import os

'''
The following function is based on this stack overflow post:
https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
Describing how to access the local IP of a device. It is used to identify which node the VM is within the topology
'''


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "Error: Unable to determine IP address"
    return ip


'''
The read_topology function takes in a file path, assuming that the file is in the correct format specified for topology.dat.
After reading the file, it iterates through the lines, converting the 3rd column (the distance) into an int and storing it into a list of lists that is returned at the end.
This function also counts the number of unique IP addresses using a set and the .update() function, returning the number of nodes that exist within the network topology
'''


def read_topology(file_path):
    topology_data = []
    unique_nodes = set()

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            parts[2] = int(parts[2])
            unique_nodes.update([parts[0], parts[1]])
            topology_data.append(parts)

    return topology_data, len(unique_nodes)


'''
This function takes in the topology data once iterated and the local ip address, then creating a topology table for the current node which is then returned as a list of lists.
The topology tables are in the following format:
    <Local IP> <Node 1>:Cost:<Next Hop> ... <Node N>:Cost:<Next Hop>
'''


def get_routing_table(ip_address, topology_data):
    node_topology = []
    for row in topology_data:
        if ip_address == row[0]:
            node_topology.append([row[1], row[2], row[1]])
        elif ip_address == row[1]:
            node_topology.append([row[0], row[2], row[0]])
    node_topology.insert(0, [ip_address])
    return node_topology


"""
Converts an IP address string to a tuple of integers to help with sorting in the clean topology function
"""


def ip_key(ip):
    return tuple(map(int, ip.split('.')))


'''
Since a topology created by the Bellman-Ford method may be out of order, this function sorts it just to make it look cleaner.
Helps things be easier to read
'''


def clean_topology(node_topology):
    header = node_topology[0]
    sorted_topology = sorted(node_topology[1:], key=lambda x: ip_key(x[0]))
    return [header] + sorted_topology


'''
This function is pretty straightforward, just logging the changes made to the topology to the logfile with the necessary formatting
Called by the main method as changes are made
'''


def log_topology(file, topology):

    entries = topology[1:]
    formatted_entries = ' '.join(
        [f"<{entry[0]}:{entry[1]}:{entry[2]}>" for entry in entries])
    file.write(formatted_entries + '\n')
    file.flush()
    os.fsync(file.fileno())


'''
This function tables in the DV arrays for the current IP address "node_topology" and "received_topology" which is a list of all the distance vectors received from the various nodes in the networks.
It then uses an implementation of Bellman_Ford based on: https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
It calls the clean topology function and log function before returning, ensuring that the returned topology is orderly and logged.
'''


def update_routing_table(node_topology, received_topology):
    current_ip = node_topology[0][0]
    distances = {current_ip: 0}
    next_hop = {current_ip: current_ip}
    for entry in node_topology[1:]:
        neighbor, cost, next = entry
        distances[neighbor] = int(cost)
        next_hop[neighbor] = next
    for routing_table in received_topology:
        for entry in routing_table[1:]:
            neighbor, cost, _ = entry
            if neighbor not in distances:
                distances[neighbor] = float('inf')
                next_hop[neighbor] = None
    edges = []
    for entry in node_topology[1:]:
        neighbor, cost, _ = entry
        edges.append((current_ip, neighbor, int(cost)))
    for routing_table in received_topology:
        sender_ip = routing_table[0][0]
        for entry in routing_table[1:]:
            neighbor, cost, _ = entry
            edges.append((sender_ip, neighbor, int(cost)))
    for _ in range(len(distances)):
        for src, dest, cost in edges:
            if distances[src] + cost < distances[dest]:
                distances[dest] = distances[src] + cost
                next_hop[dest] = next_hop[src] if src != current_ip else dest
    updated_node_topology = [[current_ip]]
    for dest in distances:
        if dest != current_ip:
            updated_node_topology.append(
                [dest, distances[dest], next_hop[dest]])
    clean_topology(updated_node_topology)
    return updated_node_topology


'''
The next 2 functions are used by the sockets when sending and receving so that my data is sent as bytes rather than as the list of lists the vector data is held as.
This is required since sockets cannot send list items.
'''


def list_of_lists_to_string(list_of_lists):
    return (';'.join(','.join(map(str, sublist))
            for sublist in list_of_lists)).ljust(256, 'x')


def string_to_list_of_lists(string):
    return [element.rstrip('x').split(',')
            for element in string.split(';') if element]


# parse input arguments
# <overlay_port>
# example: 60000
'''
Detail on the main method is provided in the design.md file
'''
if __name__ == '__main__':
    print("Started DVR")
    # the port used to send messages to neighbors
    overlay_port = int(sys.argv[1])
    current_ip = get_local_ip()
    topology_data, node_num = read_topology('topology.dat')
    node_topology = get_routing_table(current_ip, topology_data)
    file_path = f'log_{current_ip}.txt'
    received_topology = []
    log = []
    with open(file_path, 'w') as file:
        print("Logging has started")
        log_topology(file, node_topology)
        log.append(node_topology)
        print("Socket initialized")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((current_ip, overlay_port))
        s.settimeout(2)
        time.sleep(5)
        print("Sending, receiving, and calculating requisite information")
        serialized_topology = list_of_lists_to_string(node_topology)
        serialized_topology = serialized_topology.encode('utf-8')
        s.send(serialized_topology)
        for i in range(20):
            # I had to use a for loop for reasons outlined in the README but feel free to comment it out and use the below while if you want to see the issue I was having
            # while True:
            data = s.recv(256)
            data = string_to_list_of_lists(data.decode('utf-8'))
            if data in received_topology:
                time.sleep(0.5)
                s.send(serialized_topology)
            else:
                received_topology.append(data)
                node_topology = update_routing_table(
                    node_topology, received_topology)
                if node_topology not in log:
                    log.append(node_topology)
                    log_topology(file, node_topology)
                serialized_topology = list_of_lists_to_string(node_topology)
                serialized_topology = serialized_topology.encode('utf-8')
                s.send(serialized_topology)
        s.close()
        print("Socket successfully closed")
        print("Calculations finished, printing log table:")
    with open(file_path, 'r') as file:
        for line in file:
            print(line, end='')

    print("Finished")
