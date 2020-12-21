import community as community_louvain
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt


def apply_community_louvain(G):
    partition = community_louvain.best_partition(G)

    dendo = community_louvain.generate_dendrogram(G)
    highest_partition = community_louvain.partition_at_level(dendo, (len(dendo) - 1))
    communities = set(highest_partition.values())

    print(f"There are {len(communities)} communities available;")

    for community_number in communities:
        community_items = [
            x for x in highest_partition if highest_partition[x] == community_number
        ]
        print(f"Community number {community_number + 1}: {community_items}")


def show_graph_with_communities(G):
    partition = community_louvain.best_partition(G)

    pos = nx.spring_layout(G)

    # color the nodes according to their partition
    cmap = cm.get_cmap("viridis", max(partition.values()) + 1)
    nx.draw_networkx_nodes(
        G,
        pos,
        partition.keys(),
        node_size=40,
        cmap=cmap,
        node_color=list(partition.values()),
    )
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    plt.show()
