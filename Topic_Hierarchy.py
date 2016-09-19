
# coding: utf-8

# In[1]:


import time
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import codecs
import httplib
from lxml import html
import MySQLdb

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from os import listdir
from os.path import isfile, join

from collections import Counter
import matplotlib.pyplot as plt
import math
from os import walk
import operator
import sys
import networkx as nx
import collections


f = []


# # Extract Nodes at a given Level

# In[47]:

'''
    Extracts nodes present at a particular level of a graph G with root.
'''
def extract_nodes_at_level( G, level, root ):

    x = nx.shortest_path_length(G, root)
    sorted_x = sorted(x.items(), key=operator.itemgetter(1),reverse= True)
    #print sorted_x
    nodes_at_level = []
    for (node,depth) in sorted_x:
        if depth == level:
            nodes_at_level.append(node)
    return nodes_at_level



# # Calculate the Nearest node from a list of nodes for a target node

# In[48]:

def nearest_node_in_list(Graph, node, list_node):
    closest_node_list = [node]
    closest_single_node = node
    closest_distance = 9999
    first_time = 1
    #print closest_node_list

    for each_node in list_node:
        try:
            distance = nx.shortest_path_length(Graph,source = node, target= each_node)
        except Exception as e:
            #print "no distance",node,each_node
            #print e
            continue
        if distance < closest_distance:
            closest_node_list = [each_node]
            closest_single_node = each_node
            closest_distance = distance
        elif distance == closest_distance:
            closest_node_list.append(each_node)

    return closest_node_list
    #return [closest_single_node]





G=nx.Graph()
#edge_path = "./Hierarchy_Edge_listt"
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


#nodes_level = extract_nodes_at_level(G_new, level = 2, 214224)
nodes_level = extract_nodes_at_level(G_new, 2, 214224)
print "Nodes at level are:",len(nodes_level)

