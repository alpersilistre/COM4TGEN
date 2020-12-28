import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import json
import uuid


def generate_graph_from_graphwalker_json(file_name):
    with open(file_name) as f:
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
    main_model_finish_id = [
        x for x in main_model["nodes"] if x.get("name") == "v_Finish"
    ][0]["id"]
    finish_edge = [
        x for x in main_model["links"] if x.get("target") == main_model_finish_id
    ][0]

    last_vertice_id = finish_edge.get("source")
    community_last_vertice = [
        x for x in main_model["nodes"] if x.get("id") == last_vertice_id
    ][0]
    return community_last_vertice


def generate_graphwalker_json_from_model(community_number, community, main_model):
    with open("emptyModel.json") as f_main:
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

        main_model_start_id = [
            x for x in main_model["nodes"] if x.get("name") == "v_Start"
        ][0]["id"]
        main_model_start_edge = [
            x
            for x in main_model["links"]
            if x.get("source") == main_model_start_id and x.get("target") in community
        ][0]

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
        with open(community_json_name, "w", encoding="utf-8") as f_community:
            json.dump(json_data, f_community, ensure_ascii=False, indent=4)

        return community_json_name
