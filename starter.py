import snap
import numpy as np
from itertools import permutations
from matplotlib import pyplot as plt
import random

def load_graph():
    if name == "origin":
        G = snap.LoadEdgeList(snap.PNGraph, "query-url-graphdata.tsv", 0, 1)
    elif name == 'query':
		G = snap.LoadEdgeList(snap.PNGraph, "query-graphdata.tsv", 0, 1)
    else:
        raise ValueError("Invalid graph!")
    
    return G

def plot(clustering_coeffs):
    '''
    Helper plotting code for question 3.1 Feel free to modify as needed.
    '''
    plt.plot(np.linspace(0,10000,len(clustering_coeffs)), clustering_coeffs)
    plt.xlabel('Iteration')
    plt.ylabel('Average Clustering Coefficient')
    plt.title('Random edge rewiring: Clustering Coefficient')
    plt.savefig('q3_1.png', format='png')
    plt.show()

def gen_basic_features(graph):
	nodeCnt = graph.GetNodes();
	edgeCnt = graph.GetEdges();
	

    ##########################################################################

if __name__ == "__main__":
    Graph = load_graph()
    print "graph loaded"
	

