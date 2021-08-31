import time
import os.path
from graph_conversions import *
from louvain import *
from utility_functions import *
import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from subprocess import PIPE, run


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def generate_testcase_from_grapwalker(model_name, coverage_percentage=100, end_point="v_Finish"):
    model_file_path = os.path.join("json_models", model_name)

    commands = [
        "java",
        "-jar",
        "graphwalker-cli-4.3.0.jar",
        "offline",
        "-m",
        f"{model_file_path}",
        f"random(vertex_coverage({str(coverage_percentage)}) AND reached_vertex({end_point}) AND edge_coverage({str(coverage_percentage)}))",
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


def generate_vertex_testcase_from_grapwalker(model_name, remove_duplicates=False, coverage_percentage=100, end_point="v_Finish"):
    test_case = generate_testcase_from_grapwalker(model_name, coverage_percentage, end_point)
    vertex_test_cases = [x for x in test_case if x.startswith("v_")]

    test_suite = []
    last_test_case = []
    for i in range(len(vertex_test_cases)):
        if vertex_test_cases[i] == "v_Start":
            last_test_case = []
            last_test_case.append(vertex_test_cases[i])
        elif vertex_test_cases[i] == "v_Finish":
            last_test_case.append(vertex_test_cases[i])
            if remove_duplicates:
                is_equal = False
                for item in test_suite:
                    if are_arrays_equal(item, last_test_case):
                        is_equal = True

                if is_equal is False:
                    test_suite.append(last_test_case)
            else:
                test_suite.append(last_test_case)
        else:
            last_test_case.append(vertex_test_cases[i])

    return test_suite


def calculate_test_suite(test_suite, verbose=True):
    if verbose:
        print(f"Total number of test case in the test suite: {len(test_suite)}")
    total_vertex_number = 0
    for test_case in test_suite:
        total_vertex_number = total_vertex_number + len(test_case)

    if verbose:
        print(f"Total number of steps in the test suite: {total_vertex_number}")

    return len(test_suite), total_vertex_number


def calculate_communities_test_suite(communities_test_suite_list):
    test_suite_length = 0
    total_vertex_number = 0

    for community_test_suite in communities_test_suite_list:
        community_test_suite_length, community_total_vertex_number = calculate_test_suite(community_test_suite, False)
        test_suite_length = test_suite_length + community_test_suite_length
        total_vertex_number = total_vertex_number + community_total_vertex_number

    print(f"Total number of test case in the test suite: {test_suite_length}")
    print(f"Total number of steps in the test suite: {total_vertex_number}")


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


def apply_test_execution_on_model(test_suite, model, verbose=True):
    nodes_dict = {}
    for node in model["nodes"]:
        nodes_dict[node["name"]] = node["id"]

    for test_case in test_suite:
        if verbose is True:
            print(f"Test case to apply: {test_case}")
        previous_item = ""
        for item in test_case:
            if item == "v_Start":
                previous_item = nodes_dict[item]
                continue
            else:
                current_item = nodes_dict[item]
                if check_if_path_exist(model["links"], previous_item, current_item):
                    if verbose is True:
                        print(
                            f"successfully moved from {get_key_from_value_in_dict(previous_item, nodes_dict)} -> {get_key_from_value_in_dict(current_item, nodes_dict)}"
                        )
                    previous_item = nodes_dict[item]
                else:
                    if verbose is True:
                        print(
                            f"No pair found for: {get_key_from_value_in_dict(previous_item, nodes_dict)} -> {get_key_from_value_in_dict(current_item, nodes_dict)}"
                        )
                    return False

    return True


def apply_test_execution_on_community_model(communities_test_suite, model, verbose=True):
    nodes_dict = {}
    for node in model["nodes"]:
        nodes_dict[node["name"]] = node["id"]

    for community_test_suite in communities_test_suite:
        for test_case in community_test_suite:
            if verbose is True:
                print(f"Test case to apply: {test_case}")
            previous_item = ""
            is_temp_item = False
            for i in range(len(test_case)):
                item = test_case[i]

                if item == "v_Start":
                    previous_item = nodes_dict[item]
                elif item == "v_Temp":
                    is_temp_item = True
                elif is_temp_item is True:
                    current_item = nodes_dict[item]
                    if verbose is True:
                        print(
                            f"successfully moved from v_Temp -> {get_key_from_value_in_dict(current_item, nodes_dict)}"
                        )
                    previous_item = nodes_dict[item]
                    is_temp_item = False
                else:
                    current_item = nodes_dict[item]
                    if check_if_path_exist(model["links"], previous_item, current_item):
                        if verbose is True:
                            print(
                                f"successfully moved from {get_key_from_value_in_dict(previous_item, nodes_dict)} -> {get_key_from_value_in_dict(current_item, nodes_dict)}"
                            )
                        previous_item = nodes_dict[item]
                    else:
                        if verbose is True:
                            print(
                                f"No pair found for: {get_key_from_value_in_dict(previous_item, nodes_dict)} -> {get_key_from_value_in_dict(current_item, nodes_dict)}"
                            )
                        return False

    return True


def apply_model_based_testing_on_model(model_name, main_model):
    print("----")
    print(f"Applying model based testing on {model_name}")
    model_test_suite = generate_vertex_testcase_from_grapwalker(model_name)

    iteration_number = 30
    number_of_killed_mutant = 0
    number_of_lived_mutant = 0

    for i in range(iteration_number):
        mutation_model = generate_mutation_model(main_model, i)

        if (apply_test_execution_on_model(model_test_suite, mutation_model, False)) is True:
            print(f"{bcolors.WARNING}Test execution is successful. Mutant number {i + 1} can not be killed.{bcolors.ENDC}")
            number_of_lived_mutant += 1
        else:
            print(f"{bcolors.OKGREEN}Test execution is failed. Mutant number {i + 1} is killed.{bcolors.ENDC}")
            number_of_killed_mutant += 1

    print(f"{iteration_number} mutant created: {number_of_lived_mutant} mutant(s) lived, {number_of_killed_mutant} mutant(s) killed.")
    print("----")


def base_and_communities_mutant_scenario():
    model_name = "exampleModel4.json"
    eliminate_same_name_vertexes(model_name)

    main_model = generate_graph_from_graphwalker_json(model_name)

    apply_model_based_testing_on_model(model_name, main_model)

    G = json_graph.node_link_graph(main_model)

    # show_graph(G)
    # show_graph_with_communities(G)

    community_jsons = []
    communities = apply_community_louvain(G)
    community_number = 0
    for community in communities:
        community_number += 1
        community_json_name = generate_graphwalker_json_from_model(community_number, community, main_model)
        community_jsons.append(community_json_name)

        community_model = generate_graph_from_graphwalker_json(community_json_name)
        apply_model_based_testing_on_model(community_json_name, community_model)

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


def main():
    start_time = time.time()
    model_name = "ComplexModel.json"
    eliminate_same_name_vertexes(model_name)

    main_model = generate_graph_from_graphwalker_json(model_name)

    # apply_model_based_testing_on_model(model_name, main_model)
    main_model_test_suite = generate_vertex_testcase_from_grapwalker(model_name)
    print("Main model test suite result:")
    calculate_test_suite(main_model_test_suite)

    iteration_number = 30
    number_of_killed_mutant = 0
    number_of_lived_mutant = 0

    main_model_mutants = []

    for i in range(iteration_number):
        mutation_model = generate_mutation_model(main_model, i)
        main_model_mutants.append(mutation_model)

        if (apply_test_execution_on_model(main_model_test_suite, mutation_model, False)) is True:
            print(f"{bcolors.WARNING}Test execution is successful. Mutant number {i + 1} can not be killed.{bcolors.ENDC}")
            number_of_lived_mutant += 1
        else:
            print(f"{bcolors.OKGREEN}Test execution is failed. Mutant number {i + 1} is killed.{bcolors.ENDC}")
            number_of_killed_mutant += 1

    print(f"{iteration_number} mutant created: {number_of_lived_mutant} mutant(s) lived, {number_of_killed_mutant} mutant(s) killed.")
    print("----")

    G = json_graph.node_link_graph(main_model)

    communities_test_suite = []

    communities = apply_community_louvain(G)
    community_number = 0
    for community in communities:
        community_number += 1
        community_json_name, is_middle_community = generate_graphwalker_json_from_model(community_number, community, main_model)

        # community_model = generate_graph_from_graphwalker_json(community_json_name)
        community_test_cases = generate_vertex_testcase_from_grapwalker(community_json_name)

        # If the community does not start from the beginning of the main model, we will inject a temp vertex after the v_Start
        # Then when we apply model based testing, we will jump onto the entrance vertex to bypass missing path
        if is_middle_community:
            for community_test_case in community_test_cases:
                community_test_case.insert(1, "v_Temp")

        communities_test_suite.append(community_test_cases)

    print("Communities test suite result:")
    calculate_communities_test_suite(communities_test_suite)

    communities_number_of_killed_mutant = 0
    communities_number_of_lived_mutant = 0

    # Apply model based testing with communities test suite on mutant models
    for mutation_model in main_model_mutants:
        if (apply_test_execution_on_community_model(communities_test_suite, mutation_model, False)) is True:
            print(f"{bcolors.WARNING}Test execution is successful. Mutant number {mutation_model.get('graph').get('name')} can not be killed.{bcolors.ENDC}")
            communities_number_of_lived_mutant += 1
        else:
            print(f"{bcolors.OKGREEN}Test execution is failed. Mutant number {mutation_model.get('graph').get('name')} is killed.{bcolors.ENDC}")
            communities_number_of_killed_mutant += 1

    print(
        f"{iteration_number} mutant processed with communities test suite: {communities_number_of_lived_mutant} mutant(s) lived, {communities_number_of_killed_mutant} mutant(s) killed."
    )
    print("----")
    end_time = time.time()
    operation_time = end_time - start_time
    print("Runtime of the program is: {:.2f} seconds".format(operation_time))


if __name__ == "__main__":
    main()
