import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import os.path
import json
import uuid
import random
import copy


def generate_graph_from_graphwalker_json(file_name):
    file_path = os.path.join("json_models", file_name)

    with open(file_path) as f:
        json_data = json.load(f)
        model_data = json_data.get("models")[0]
        model = {
            "directed": False,
            "multigraph": False,
            "graph": {"name": model_data["name"]},
            "nodes": [],
            "links": [],
        }

        for vertice in model_data["vertices"]:
            vertice_dict = {
                "id": vertice["id"],
                "name": vertice["name"],
                "x": vertice["properties"]["x"],
                "y": vertice["properties"]["y"],
            }
            model["nodes"].append(vertice_dict)

        for edge in model_data["edges"]:
            edge_dict = {
                "source": edge["sourceVertexId"],
                "target": edge["targetVertexId"],
                "id": edge["id"],
                "name": edge["name"],
            }
            model["links"].append(edge_dict)

        return model


def generate_mutation_model(main_model, mutation_number):
    mutated_model = copy.deepcopy(main_model)
    model_name = mutated_model["graph"]["name"]
    mutated_model["graph"]["name"] = f"{model_name}-{mutation_number}"

    random_number = random.randint(1, 2)
    if random_number == 1:
        delete_link(mutated_model)
    elif random_number == 2:
        delete_node(mutated_model)

    return mutated_model


def delete_link(model):
    """Delete a random link from the model to create a mutant by Delete(edge)
    Do not delete links that start and end nodes are part of.
    """

    start_node = next((e for e in model["nodes"] if e["name"] == "v_Start"), None)
    finish_node = next((e for e in model["nodes"] if e["name"] == "v_Finish"), None)

    selected_link_id = ""
    while selected_link_id == "":
        random_link_number = random.randint(0, len(model["links"]) - 1)
        temp_link = model["links"][random_link_number]
        if (
            temp_link["source"] != start_node["id"]
            and temp_link["source"] != finish_node["id"]
            and temp_link["target"] != start_node["id"]
            and temp_link["target"] != finish_node["id"]
        ):
            selected_link_id = temp_link["id"]

    new_links = [x for x in model["links"] if x["id"] != selected_link_id]
    model["links"] = new_links


def delete_node(model):
    """Delete a random node from the model to create a mutant by Delete(vertex)
    Do not delete start and end nodes.
    """

    selected_node_id = ""
    while selected_node_id == "":
        random_node_number = random.randint(0, len(model["nodes"]) - 1)
        temp_node = model["nodes"][random_node_number]
        if temp_node["name"] != "v_Start" and temp_node["name"] != "v_Finish":
            selected_node_id = temp_node["id"]

    new_links = [x for x in model["links"] if (x["source"] != selected_node_id and x["target"] != selected_node_id)]
    model["links"] = new_links


def get_model_vertice(id, main_model):
    vertice_dict = {"id": id, "name": "", "properties": {"x": 0, "y": 0}}
    vertice = [x for x in main_model["nodes"] if x.get("id") == id]

    vertice_dict["name"] = vertice[0]["name"]
    vertice_dict["properties"]["x"] = vertice[0]["x"]
    vertice_dict["properties"]["y"] = vertice[0]["y"]

    return vertice_dict


def get_model_edges(source_id, main_model):
    empty_edge_dict = {
        "id": "",
        "name": "",
        "sourceVertexId": source_id,
        "targetVertexId": "",
    }
    edges = [x for x in main_model["links"] if x.get("source") == source_id]
    edge_dict_list = []

    for edge in edges:
        edge_dict = empty_edge_dict.copy()
        edge_dict["name"] = edge["name"]
        edge_dict["sourceVertexId"] = edge["source"]
        edge_dict["targetVertexId"] = edge["target"]
        edge_dict["id"] = edge["id"]
        edge_dict_list.append(edge_dict)

    return edge_dict_list


def get_community_last_vertice(community, main_model):
    main_model_finish_id = [x for x in main_model["nodes"] if x.get("name") == "v_Finish"][0]["id"]
    finish_edge = [x for x in main_model["links"] if x.get("target") == main_model_finish_id][0]

    last_vertice_id = finish_edge.get("source")
    community_last_vertice = [x for x in main_model["nodes"] if x.get("id") == last_vertice_id][0]
    return community_last_vertice


def generate_graphwalker_json_from_model(community_number, community, main_model):
    empty_model_json_file = os.path.join("json_models", "emptyModel.json")

    with open(empty_model_json_file) as f_main:
        json_data = json.load(f_main)
        model_data = json_data.get("models")[0]

        model_data["id"] = str(uuid.uuid4())
        model_data["name"] = f"community-{community_number}"
        # Create guid for the start node
        start_element_id = str(uuid.uuid4())
        model_data["startElementId"] = start_element_id
        model_data["vertices"][0]["id"] = start_element_id
        # Create guid for the end node
        finish_element_id = str(uuid.uuid4())
        model_data["vertices"][1]["id"] = finish_element_id
        json_data["selectedElementId"] = finish_element_id

        main_model_start_id = [x for x in main_model["nodes"] if x.get("name") == "v_Start"][0]["id"]
        main_model_start_edge = [x for x in main_model["links"] if x.get("source") == main_model_start_id and x.get("target") in community][0]

        community_start_edge = {
            "id": str(uuid.uuid4()),
            "name": main_model_start_edge.get("name"),
            "sourceVertexId": start_element_id,
            "targetVertexId": main_model_start_edge.get("target"),
        }
        model_data["edges"].append(community_start_edge)

        for vertice_id in community:
            vertice = get_model_vertice(vertice_id, main_model)
            edges = get_model_edges(vertice_id, main_model)
            model_data["vertices"].append(vertice)
            for edge in edges:
                model_data["edges"].append(edge)

        community_last_vertice = get_community_last_vertice(community, main_model)
        model_data["vertices"].append(community_last_vertice)
        community_end_edge = {
            "id": str(uuid.uuid4()),
            "name": "e_Finish",
            "sourceVertexId": community_last_vertice.get("id"),
            "targetVertexId": finish_element_id,
        }
        model_data["edges"].append(community_end_edge)

        # Pseudo edge from finish to start
        community_pseudo_edge = {
            "id": str(uuid.uuid4()),
            "name": "e_Pseudo",
            "sourceVertexId": finish_element_id,
            "targetVertexId": start_element_id,
        }
        model_data["edges"].append(community_pseudo_edge)

        community_json_name = f"community-{community_number}.json"
        community_json_file_path = os.path.join("json_models", community_json_name)

        with open(community_json_file_path, "w", encoding="utf-8") as f_community:
            json.dump(json_data, f_community, ensure_ascii=False, indent=4)

        return community_json_name
