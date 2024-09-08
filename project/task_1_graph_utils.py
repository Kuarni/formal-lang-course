from typing import List, Tuple
from dataclasses import dataclass
import cfpq_data
import networkx as nx


def get_graph(name: str):
    graph = cfpq_data.graph_from_csv(cfpq_data.download(name))
    return graph


@dataclass
class GraphData:
    number_of_nodes: int
    number_of_edges: int
    labels: List[any]


def get_graph_data(name: str) -> GraphData:
    graph = get_graph(name)
    return GraphData(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        cfpq_data.get_sorted_labels(graph),
    )


def save_pydot_graph(graph, save_path: str):
    nx.drawing.nx_pydot.write_dot(graph, save_path)


def create_and_save_graph(
    cycle_1_nodes: int, cycle_2_nodes: int, labels: Tuple[str, str], save_path: str
):
    graph = cfpq_data.labeled_two_cycles_graph(
        cycle_1_nodes, cycle_2_nodes, labels=labels
    )
    save_pydot_graph(graph, save_path)
