
# coding: utf-8

# In[1]:


#import MySQLdb

#import matplotlib.pyplot as plt
import operator

import networkx as nx

f = []


# # Extract Nodes at a given Level

# In[47]:

'''
    Extracts nodes present at a particular level of a graph G with root.
'''


def extract_nodes_at_level(G, root, level):

    x = nx.shortest_path_length(G, root)
    sorted_x = sorted(x.items(), key=operator.itemgetter(1),reverse= True)
    #print sorted_x
    nodes_at_level = []
    for (node,depth) in sorted_x:
        if depth == level:
            nodes_at_level.append(node)
    return nodes_at_level


# Function to return the nodes which are at nearest distance to node in list_node in the Graph
def nearest_node_in_list(Graph, node, list_node):
    closest_node_list = [node]
    closest_single_node = node
    closest_distance = 9999
    first_time = 1
    #print closest_node_list

    for each_node in list_node:
        try:
            distance = nx.shortest_path_length(Graph,source = node, target= each_node)
            #print "distance" + str(distance)
        except Exception as e:
            #print "no distance",node,each_node
            print e
            continue
        if distance < closest_distance:
            #print "Found a node with shorter distance"
            closest_node_list = [each_node]
            closest_single_node = each_node
            closest_distance = distance
        elif distance == closest_distance:
            closest_node_list.append(each_node)

    return closest_node_list



    #return [closest_single_node]


G = nx.Graph()
edge_path = "./Topic_Hierarchy_Edge_List.txt"
with open(edge_path) as fp:
    for line in fp:
        parts = line.split()
        part1 = int(parts[0])
        part2 = int(parts[1])
        G.add_edge(part1,part2)

print "Nodes and Edges read.."
largest_cc = max(nx.connected_components(G), key=len)
G_new = nx.subgraph(G,largest_cc)

#print "here",nearest_node_in_list(G_new, 214224,[1,3,110611,2,240414])


nodes_level = extract_nodes_at_level(G_new, 90223, level = 2)
#nodes_level = extract_nodes_at_level(G_new, 2, 2)
print "Nodes at level are:",len(nodes_level)
#print "Node ids"
print nodes_level


user_topic_dict = {}
user_list = [0 for x in range(len(nodes_level))]
#print user_list
node_list = nearest_node_in_list(G_new, 18542, nodes_level)
print "Nodes nearest to 200 are:"
print node_list
for node in node_list:
    print node
    print nodes_level.index(node)
    user_list[nodes_level.index(node)] += 1
print user_list
