import time
from graph_conversions import *
from louvain import *
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from subprocess import PIPE, run


def show_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.show()


def main():
    G = nx.random_k_out_graph(15, 3, 1, False)
    show_graph(G)
    # show_graph_with_communities(G)


if __name__ == "__main__":
    main()
