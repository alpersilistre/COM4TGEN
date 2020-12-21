from graphwalker_to_networkx_graph import *
from louvain import *
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from subprocess import PIPE, run


def generate_testcase_from_grapwalker(model_name, end_point="v_UserLoggedIn"):
    commands = [
            "java",
            "-jar",
            "graphwalker-cli-4.3.0.jar",
            "offline",
            "-m",
            f"{model_name}",
            f"random(reached_vertex({end_point}))",
        ]
    result = run(commands, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    result_list = result.stdout.split("\n")
    test_case = []

    for item in list(filter(None, result_list)):
        result_dict = eval(item)
        test_case.append(result_dict["currentElementName"])

    return test_case


def show_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.show()


def main():
    model = generate_graph_from_graphwalker_json("LoginSignUpForm.json")
    G = json_graph.node_link_graph(model)

    show_graph(G)
    # show_graph_with_communities(G)
    # apply_community_louvain(G)
    # test_case = generate_testcase_from_grapwalker("LoginSignUpForm.json")
    # print(test_case)


if __name__ == "__main__":
    main()
