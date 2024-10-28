from itertools import product

import networkx as nx
from pyformlang.cfg import Variable, Production, Epsilon, CFG, Terminal


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    return CFG(
        start_symbol=cfg.start_symbol,
        productions=cfg.to_normal_form().productions
        | {
            Production(Variable(var.value), [Epsilon()])
            for var in cfg.get_nullable_symbols()
        },
    ).remove_useless_symbols()


def __hellings_init(wnf_cfg: CFG, graph: nx.DiGraph):
    result = set()
    for u, v, data in graph.edges(data=True):
        label = data.get("label")
        if label is not None:
            for production in wnf_cfg.productions:
                if len(production.body) == 1 and isinstance(
                    production.body[0], Terminal
                ):
                    terminal = production.body[0].value
                    if terminal == label:
                        result.add((u, production.head, v))
    result |= {
        (node, var, node)
        for node, var in product(graph.nodes, wnf_cfg.get_nullable_symbols())
    }
    return result


def __hellings_update_extend(wnf_cfg: CFG, result):
    added = True
    while added:
        added = False
        new_results = set()

        for v1, B, v2 in result:
            for v2_, C, v3 in result:
                if v2 == v2_:
                    for production in wnf_cfg.productions:
                        if (
                            len(production.body) == 2
                            and production.body[0] == B
                            and production.body[1] == C
                        ):
                            new_triple = (v1, production.head, v3)
                            if new_triple not in result:
                                new_results.add(new_triple)
                                added = True

        result |= new_results


def __hellings_filter(wnf_cfg: CFG, start_nodes, final_nodes, results):
    filtered = set()
    for u, var, v in results:
        if var == wnf_cfg.start_symbol:
            if (not start_nodes or u in start_nodes) and (
                not final_nodes or v in final_nodes
            ):
                filtered.add((u, v))
    return filtered


def hellings_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    weak_normal_form = cfg_to_weak_normal_form(cfg)

    cfpq_results = __hellings_init(weak_normal_form, graph)

    __hellings_update_extend(weak_normal_form, cfpq_results)

    return __hellings_filter(weak_normal_form, start_nodes, final_nodes, cfpq_results)
