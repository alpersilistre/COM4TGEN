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
    empty_edge_dict = {"id": "", "name": "", "sourceVertexId": source_id, "targetVertexId": ""}
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
        model_data["vertices"][1]["id"] = str(uuid.uuid4())

        for item in community:
            vertice = get_model_vertice(item, main_model)
            edges = get_model_edges(item, main_model)
            model_data["vertices"].append(vertice)
            for edge in edges:
                model_data["edges"].append(edge)

        with open(
            f"community-{community_number}.json", "w", encoding="utf-8"
        ) as f_community:
            json.dump(json_data, f_community, ensure_ascii=False, indent=4)
