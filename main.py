from graphwalker_to_networkx_graph import *
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph


def show_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.show()


def main():
    model = generate_graph_from_graphwalker_json("LoginSignUpForm.json")
    G = json_graph.node_link_graph(model)

    show_graph(G)


if __name__ == "__main__":
    main()
