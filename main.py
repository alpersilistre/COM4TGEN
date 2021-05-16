import time
import os.path
from graph_conversions import generate_graph_from_graphwalker_json
from graph_conversions import generate_graphwalker_json_from_model
from louvain import apply_community_louvain
from louvain import show_graph_with_communities
from utility_functions import *
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from subprocess import PIPE, run


def generate_testcase_from_grapwalker(model_name, end_point="v_Finish"):
    model_file_path = os.path.join("json_models", model_name)

    commands = [
        "java",
        "-jar",
        "graphwalker-cli-4.3.0.jar",
        "offline",
        "-m",
        f"{model_file_path}",
        f"random(vertex_coverage(100) AND reached_vertex({end_point}))",
    ]
    result = run(commands, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    if result.stderr:
        raise ValueError(result.stderr)

    result_list = result.stdout.split("\n")
    test_case = []

    for item in list(filter(None, result_list)):
        result_dict = eval(item)
        test_case.append(result_dict["currentElementName"])

    return test_case


def generate_vertex_testcase_from_grapwalker(model_name, end_point="v_Finish"):
    test_case = generate_testcase_from_grapwalker(model_name, end_point)
    vertex_test_cases = [x for x in test_case if x.startswith("v_")]

    test_suite = []
    last_test_case = []
    for i in range(len(vertex_test_cases)):
        if vertex_test_cases[i] == "v_Start":
            last_test_case = []
            last_test_case.append(vertex_test_cases[i])
        elif vertex_test_cases[i] == "v_Finish":
            is_equal = False
            last_test_case.append(vertex_test_cases[i])

            for item in test_suite:
                if are_arrays_equal(item, last_test_case):
                    is_equal = True

            if is_equal is False:
                test_suite.append(last_test_case)
        else:
            last_test_case.append(vertex_test_cases[i])

    return test_suite


def show_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.show()


def apply_test_generation_on_main_model(model_name):
    total_time = 0

    start_time = time.time()
    test_case = generate_testcase_from_grapwalker(model_name)
    end_time = time.time()
    operation_time = end_time - start_time
    formatted_operation_time = "{:.2f}".format(operation_time)
    total_time = total_time + float("{:.2f}".format(operation_time))
    iteration_number = 1
    print(f"Runtime of the iteration {iteration_number} is: {formatted_operation_time} seconds")

    # for val in range(10):
    # print(f"Test result: {test_case}")

    # print(f"Average runtime: {total_time / 10}")
    print(f"Runtime: {total_time}, test suite size: {len(test_case)}")


def check_if_path_exist(links, source, target):
    for link in links:
        if link["source"] == source and link["target"] == target:
            return True

    return False


def apply_test_execution_on_model(test_suite, model):
    nodes_dict = {}
    for node in model["nodes"]:
        nodes_dict[node["name"]] = node["id"]

    for test_case in test_suite:
        print(f"Test case to apply: {test_case}")
        previous_item = ""
        for item in test_case:
            if item == "v_Start":
                previous_item = nodes_dict[item]
                continue
            else:
                current_item = nodes_dict[item]
                if check_if_path_exist(model["links"], previous_item, current_item):
                    print(
                        f"successfully moved from {get_key_from_value_in_dict(previous_item, nodes_dict)} -> {get_key_from_value_in_dict(current_item, nodes_dict)}"
                    )
                    previous_item = nodes_dict[item]
                else:
                    print(f"No pair found for: {nodes_dict[previous_item]} -> {nodes_dict[current_item]}")
                    return False

    return True


def main():
    model_name = "mutateModel.json"
    main_model_test_suite = generate_vertex_testcase_from_grapwalker(model_name)

    main_model = generate_graph_from_graphwalker_json(model_name)
    if(apply_test_execution_on_model(main_model_test_suite, main_model)) is True:
        print("Test execution is successful.")
    else:
        print("Test execution is failed.")
    # G = json_graph.node_link_graph(main_model)

    # show_graph(G)
    # show_graph_with_communities(G)

    # community_jsons = []
    # communities = apply_community_louvain(G)
    # community_number = 0
    # for community in communities:
    #     community_number = community_number + 1
    #     community_json_name = generate_graphwalker_json_from_model(
    #         community_number, community, main_model
    #     )
    #     community_jsons.append(community_json_name)

    # for json_file in community_jsons:
    #     print(f"Test generation for {json_file}:")
    #     apply_test_generation_on_main_model(json_file)

    # start_time = time.time()
    # test_case = generate_testcase_from_grapwalker("ExampleModel.json")
    # end_time = time.time()
    # operation_time = end_time - start_time
    # print("Runtime of the program is: {:.2f} seconds".format(operation_time))
    # print(f"Test suite lenght: {len(test_case)}")
    # print(test_case)

    # apply_test_generation_on_main_model("LoginSignUpForm.json")


if __name__ == "__main__":
    main()
