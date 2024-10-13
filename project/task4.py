from collections import defaultdict
from functools import reduce
from itertools import product
from typing import Dict
from networkx import MultiDiGraph
from pyformlang.finite_automaton import Symbol
import scipy.sparse as sp

from project.task2 import regex_to_dfa, graph_to_nfa
from project.task3 import AdjacencyMatrixFA


class MsBfsRpq:
    __matrix_type: type(sp.spmatrix)
    __adj_dfa: AdjacencyMatrixFA
    __adj_nfa: AdjacencyMatrixFA
    __shift: int
    __intersected_symbols: set[Symbol]
    __adj_united: Dict[Symbol, type(sp.spmatrix)]
    __init_front: type(sp.spmatrix)
    __front_left: type(sp.spmatrix)

    def __unite_matrices(self) -> dict[Symbol, type(sp.spmatrix)]:
        return {
            symbol: sp.block_diag(
                (
                    self.__adj_dfa.adj_matrices[symbol],
                    self.__adj_nfa.adj_matrices[symbol],
                )
            )
            for symbol in self.__intersected_symbols
        }

    def __get_init_front(self) -> type(sp.spmatrix):
        left_vector = sp.identity(self.__shift, dtype=bool)

        vectors = []
        for nfa_state_num in range(len(self.__adj_nfa.start_states)):
            right_vector = self.__matrix_type(
                (self.__shift, self.__adj_nfa.states_number), dtype=bool
            )
            for i in self.__adj_dfa.start_states:
                right_vector[i, self.__start_states_list[nfa_state_num]] = True

            vectors.append(sp.block_array([[left_vector, right_vector]]))

        return self.__matrix_type(
            reduce(lambda a, b: sp.block_array([[a], [b]]), vectors)
        )

    def __init__(
        self,
        adj_dfa: AdjacencyMatrixFA,
        adj_nfa: AdjacencyMatrixFA,
        matrix_type=sp.csr_matrix,
    ):
        self.__matrix_type = matrix_type
        self.__adj_dfa = adj_dfa
        self.__adj_nfa = adj_nfa
        self.__start_states_list = list(adj_nfa.start_states)
        self.__shift = self.__adj_dfa.states_number
        self.__intersected_symbols = set(
            self.__adj_dfa.adj_matrices.keys()
        ).intersection(self.__adj_nfa.adj_matrices.keys())
        self.__adj_united = self.__unite_matrices()
        self.__init_front = self.__get_init_front()
        self.__front_left = self.__init_front[:, : self.__shift]

    def __update_front(self, front_right: sp.spmatrix) -> type(sp.spmatrix):
        def front_mul_matrix(cur_front, matrix) -> type(sp.spmatrix):
            mul = self.__matrix_type(cur_front @ matrix)
            diag_front_right = self.__matrix_type(front_right.shape, dtype=bool)

            for i, j in zip(*mul[:, : self.__shift].nonzero()):
                diag_front_right[i // self.__shift * self.__shift + j, :] += mul[
                    i, self.__shift :
                ]
            return diag_front_right

        front = sp.block_array([[self.__front_left, front_right]])
        updated_front = reduce(
            lambda vector, matrix: vector + front_mul_matrix(front, matrix),
            self.__adj_united.values(),
            self.__matrix_type(front_right.shape, dtype=bool),
        )

        return updated_front

    def __visited_to_dict(self, visited: sp.spmatrix) -> dict[int, set[int]]:
        start_to_reachable = defaultdict(set)
        for start_state, final_state in product(
            range(len(self.__start_states_list)), self.__adj_dfa.final_states
        ):
            states_reachable_from_end = set(
                visited[start_state * self.__shift + final_state, :].nonzero()[1]
            )
            start_to_reachable[self.__start_states_list[start_state]].update(
                states_reachable_from_end
            )
        return start_to_reachable

    def __ms_bfs(self) -> dict[int, set[int]]:
        front_right = self.__matrix_type(
            self.__init_front[:, self.__shift :], dtype=bool
        )
        visited = self.__matrix_type(front_right, dtype=bool)

        while front_right.count_nonzero():
            front_right = self.__update_front(front_right)
            front_right = front_right > visited
            visited += front_right

        return self.__visited_to_dict(visited)

    def __call__(self) -> dict[int, set[int]]:
        return self.__ms_bfs()


def ms_bfs_based_rpq(
    regex: str,
    graph: MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
    matrix_type=sp.csr_matrix,
) -> set[tuple[int, int]]:
    regex_dfa = regex_to_dfa(regex)
    adj_dfa = AdjacencyMatrixFA(regex_dfa, matrix_type)
    graph_nfa = graph_to_nfa(graph, start_nodes, final_nodes)
    adj_nfa = AdjacencyMatrixFA(graph_nfa, matrix_type)

    result = MsBfsRpq(adj_dfa, adj_nfa, matrix_type)()

    retrieved_states = {
        (start, final)
        for start, final in product(graph_nfa.start_states, graph_nfa.final_states)
        if adj_nfa.states_to_num[final] in result[adj_nfa.states_to_num[start]]
    }
    return retrieved_states
