import networkx as nx
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import json


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
            vertice_dict = {"id": vertice["id"], "name": vertice["name"]}
            model["nodes"].append(vertice_dict)

        for edge in model_data["edges"]:
            edge_dict = {
                "source": edge["sourceVertexId"],
                "target": edge["targetVertexId"],
            }
            model["links"].append(edge_dict)

        return model
