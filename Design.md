[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/sJyArgKF)
# CSEE 4119 Spring 2024, Assignment 3
## Aarya Agarwal
## GitHub username: AaryaA31



My Bellman-Ford implementation was heavily based on the descriptions of the algorithm found at the following link:
https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
I also refered to the textbook for a better understanding of the actual protocol

One thing of note is that I only logged to the log when there was a change in the routing table, not everytime I recevied new information. This helps keep the logs a lot cleaner in my opinion. I also made it so that the log prints at the very end in case you don't feel like checking each individual node for the log information.

I included progress print statements throughout my main method to keep the tester informed of which part of the process each node has reached. 

Interally, I stored the vector tables as a list of lists, converting to and from a string while sending. By using a list of lists I found it far easier to navigate when I needed to index something. The first entry in the list was always the ip of the node sending its table to the overlay.

This is the format for the distance vector tables I was sending:

[[sender_ip][<node_1>:<cost_1>:<next_hop_1>], ... ,[<node_n>:<cost_n>:<next_hop_n>]]
While it can be said that next hop is not needed, I sent it anyways to keep the format consistent with the logging just to simplify.
The data was sent as a string and was always sent with fixed length of 256 by appending 'x' as necessary to the end of the string. This helped with recv stability in my opinion as we always knew how many bits to expect.

My main method was as follows in psuedo code with commentary:

Start Program
    Print "Started DVR"
    Set overlay_port to first command line argument converted to integer
    Get current IP address
    Read topology from 'topology.dat' and store in topology_data and node_num
    Get routing table for current IP from topology_data
    Set file_path to log file name using current IP
    Initialize received_topology and log lists
    Open file with path file_path for writing
        Print "Logging has started"
        Log current routing table to file
        Add current routing table to log list
        Print "Socket initialized"
        Create a TCP socket
        Connect socket to current IP and overlay port
        Set socket timeout to 2 seconds
        Sleep for 5 seconds
        Print "Sending, receiving, and calculating requisite information"
        Convert node_topology to a string and encode to bytes
        Send serialized topology over socket
        Loop 20 times
            Receive data from socket (up to 256 bytes)
            Convert received data from bytes to string and then to list format
            If data is already in received_topology
                Sleep for 0.5 seconds
                Send serialized topology
            Else
                Add data to received_topology
                Update node_topology with received_topology
                If updated node_topology is not in log
                    Add updated node_topology to log
                    Log updated node_topology to file
                Convert updated node_topology to a string and encode to bytes
                Send serialized topology
        Close socket
        Print "Socket successfully closed"
        Print "Calculations finished, printing log table:"
    Open file with path file_path for reading
        Print each line in file
    Print "Finished"
End Program

It is fairly logical and minimizes the number of times the "update_node_topology" function is called. NOTE: I use topology to refer to the vector tables since it is a form of topology, just not a full network topology.


