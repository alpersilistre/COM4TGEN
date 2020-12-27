import community as community_louvain
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt


def get_start_and_end_nodes(G):
    start_node_id = ""
    end_node_id = ""

    for id, obj in G._node.items():
        if obj["name"] == "v_Start":
            start_node_id = id
        elif obj["name"] == "v_Finish":
            end_node_id = id

    return start_node_id, end_node_id


def apply_community_louvain(G):
    start_node_id, end_node_id = get_start_and_end_nodes(G)

    partition = community_louvain.best_partition(G)

    dendo = community_louvain.generate_dendrogram(G)
    highest_partition = community_louvain.partition_at_level(dendo, (len(dendo) - 1))
    communities = set(highest_partition.values())

    print(f"Communities;")

    list_of_communities = []

    community_count = 0
    for community_number in communities:
        community_items = [
            x for x in highest_partition if highest_partition[x] == community_number
        ]
        if start_node_id in community_items or end_node_id in community_items:
            continue
        list_of_communities.append(community_items)
        community_count = community_count + 1
        print(f"Community number {community_count}: {community_items}")

    return list_of_communities


def show_graph_with_communities(graph):
    if graph.is_directed() is True:
        G = graph.to_undirected()
    else:
        G = graph

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
