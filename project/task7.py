from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List
import networkx as nx
from pyformlang.cfg import CFG, Terminal, Variable
from scipy.sparse import csr_matrix
from project.task6 import cfg_to_weak_normal_form


@dataclass
class __AlgoData:
    def __init__(self, wnf, graph, matrix_type):
        self.wnf: CFG = wnf
        self.graph: nx.DiGraph = graph
        self.nodes_amount = graph.number_of_nodes()
        self.index_to_node = list(graph.nodes())
        self.node_to_index = {node: idx for idx, node in enumerate(self.index_to_node)}
        self.matrix_type = matrix_type


def __init_var_matrices(adata: __AlgoData):
    var_matrices = defaultdict(lambda: adata.matrix_type((adata.nodes_amount, adata.nodes_amount), dtype=bool))
    for u, v, data in adata.graph.edges(data=True):
        label = data.get("label")
        if label is not None:
            for production in adata.wnf.productions:
                if len(production.body) == 1 and isinstance(production.body[0], Terminal):
                    terminal = production.body[0].value
                    if terminal == label:
                        head = production.head
                        var_matrices[head][adata.node_to_index[u], adata.node_to_index[v]] = True
    return var_matrices


def __add_nullable(adata: __AlgoData, var_matrices):
    nullable = adata.wnf.get_nullable_symbols()
    for node in adata.graph.nodes:
        for var in nullable:
            var = Variable(var.value)
            var_matrices[var][adata.node_to_index[node], adata.node_to_index[node]] = True


def __matrix_hellings(adata: __AlgoData, var_matrices):
    added = True
    while added:
        added = False
        for production in adata.wnf.productions:
            if len(production.body) == 2:
                B = Variable(production.body[0].value)
                C = Variable(production.body[1].value)
                head = production.head
                if B in var_matrices and C in var_matrices:
                    new_mat = var_matrices[B] @ var_matrices[C]

                    for u, v in zip(*new_mat.nonzero()):
                        if not var_matrices[head][u, v]:
                            var_matrices[head][u, v] = True
                            added = True


def __get_results(adata: __AlgoData, var_matrices, start_nodes, final_nodes):
    result_pairs = set()
    start_symbol = adata.wnf.start_symbol
    if start_symbol in var_matrices:
        result_pairs |= {(u, v) for u, v in
                         map(lambda pair: map(lambda i: adata.index_to_node[i], pair),
                             zip(*var_matrices[start_symbol].nonzero())) if (not start_nodes or u in start_nodes) and (
                                 not final_nodes or v in final_nodes
                         )}
    return result_pairs


def matrix_based_cfpq(
        cfg: CFG,
        graph: nx.DiGraph,
        start_nodes: set[int] = None,
        final_nodes: set[int] = None,
        matrix_type=csr_matrix
) -> set[tuple[int, int]]:
    weak_normal_form = cfg_to_weak_normal_form(cfg)
    adata = __AlgoData(weak_normal_form, graph, matrix_type)

    var_matrices = __init_var_matrices(adata)

    __add_nullable(adata, var_matrices)

    __matrix_hellings(adata, var_matrices)

    return __get_results(adata, var_matrices, start_nodes, final_nodes)
