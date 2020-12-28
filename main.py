import time
from graph_conversions import *
from louvain import *
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from subprocess import PIPE, run


def generate_testcase_from_grapwalker(model_name, end_point="v_Finish"):
    commands = [
        "java",
        "-jar",
        "graphwalker-cli-4.3.0.jar",
        "offline",
        "-m",
        f"{model_name}",
        f"random(vertex_coverage(100) AND reached_vertex({end_point}))",
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


def apply_test_generation_on_main_model(model_name):
    total_time = 0

    for val in range(10):
        start_time = time.time()
        test_case = generate_testcase_from_grapwalker(model_name)
        end_time = time.time()
        operation_time = end_time - start_time
        formatted_operation_time = "{:.2f}".format(operation_time)
        total_time = total_time + float("{:.2f}".format(operation_time))
        iteration_number = val + 1
        print(
            f"Runtime of the iteration {iteration_number} is: {formatted_operation_time} seconds"
        )

    print(f"Average runtime: {total_time / 10}")


def main():
    # generate_graphwalker_json_from_model("1")
    main_model = generate_graph_from_graphwalker_json("LoginSignUpForm.json")
    G = json_graph.node_link_graph(main_model)

    # show_graph(G)
    # show_graph_with_communities(G)
    community_jsons = []
    communities = apply_community_louvain(G)
    community_number = 0
    for community in communities:
        community_number = community_number + 1
        community_json_name = generate_graphwalker_json_from_model(
            community_number, community, main_model
        )
        community_jsons.append(community_json_name)

    for json_file in community_jsons:
        print(f"Test generation for {json_file}:")
        apply_test_generation_on_main_model(json_file)

    # start_time = time.time()
    # test_case = generate_testcase_from_grapwalker("LoginSignUpForm.json")
    # end_time = time.time()
    # operation_time = end_time - start_time
    # print("Runtime of the program is: {:.2f} seconds".format(operation_time))
    # print(test_case)

    # apply_test_generation_on_main_model("LoginSignUpForm.json")


if __name__ == "__main__":
    main()
