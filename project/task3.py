from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, List, Optional, Self
from networkx import MultiDiGraph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol
import scipy.sparse as sp

from project.task2 import regex_to_dfa, graph_to_nfa


class AdjacencyMatrixFA:
    _matrix_type: type(sp.spmatrix)
    _adj_matrices: dict[Symbol, type(sp.spmatrix)]
    _states_number: int
    _start_states: set[int]
    _final_states: set[int]
    _states_to_num: dict[State, int]

    @staticmethod
    def __enumerate_value(value) -> dict[Any, int]:
        return {val: idx for idx, val in enumerate(value)}

    def __get_symbol_adj_matrix_dict(self, nfa) -> dict[Symbol, sp.spmatrix]:
        symbol_state = defaultdict(
            lambda: self._matrix_type((len(nfa.states), len(nfa.states)), dtype=bool)
        )
        for start_state, value in nfa.to_dict().items():
            for symbol, end_states in value.items():
                start_state_int = self._states_to_num[start_state]
                if type(end_states) is State:
                    end_states = {end_states}
                for end_st in end_states:
                    end_state_int = self._states_to_num[end_st]
                    symbol_state[symbol][start_state_int, end_state_int] = True
        return symbol_state

    def __init__(
        self, nfa: Optional[NondeterministicFiniteAutomaton], matrix_type=sp.csr_matrix
    ):
        self._matrix_type = matrix_type
        self._adj_matrices = dict()
        if nfa is None:
            self._states_number = 0
            self._start_states = set()
            self._final_states = set()
            return

        self._states_to_num = self.__enumerate_value(nfa.states)

        self._states_number = len(nfa.states)

        self._start_states = set(self._states_to_num[i] for i in nfa.start_states)
        self._final_states = set(self._states_to_num[i] for i in nfa.final_states)

        self._adj_matrices = self.__get_symbol_adj_matrix_dict(nfa)

    def __dfs_find_path(self, word: Iterable[Symbol]):
        @dataclass
        class Configuration:
            word: List[Symbol]
            state: int

        stack = [
            Configuration(list(word), start_state) for start_state in self._start_states
        ]

        while len(stack):
            cur_conf = stack.pop()

            if not len(cur_conf.word):
                if cur_conf.state in self._final_states:
                    return True
                continue

            next_symbol = cur_conf.word[0]
            if next_symbol not in self._adj_matrices.keys():
                continue

            for i in range(self._states_number):
                if self._adj_matrices[next_symbol][cur_conf.state, i]:
                    stack.append(Configuration(cur_conf.word[1:], i))

        return False

    def accepts(self, word: Iterable[Symbol]) -> bool:
        return self.__dfs_find_path(word)

    def transitive_closure(self) -> type(sp.spmatrix):
        sum_matrix = self._matrix_type(sum(self._adj_matrices.values()))
        sum_matrix.setdiag(True)
        res = sp.linalg.matrix_power(sum_matrix, self._states_number)
        return res

    def is_empty(self) -> bool:
        if not self._adj_matrices:
            return True
        transitive_closure_matrix = self.transitive_closure()

        return not any(
            transitive_closure_matrix[s, e]
            for s, e in product(self._start_states, self._final_states)
        )

    @classmethod
    def from_intersect(
        cls, automaton1: Self, automaton2: Self, matrix_type=sp.csr_matrix
    ):
        instance = cls(None, matrix_type=matrix_type)
        united_syms = [
            sym
            for sym in set(automaton1._adj_matrices.keys()).intersection(
                automaton2._adj_matrices.keys()
            )
        ]

        def get_kron_spare(matrix1, matrix2):
            return instance._matrix_type(sp.kron(matrix1, matrix2))

        instance._adj_matrices = {
            sym: get_kron_spare(
                automaton1._adj_matrices[sym], automaton2._adj_matrices[sym]
            )
            for sym in united_syms
        }

        def state_to_num(st1, st2):
            return st1 * automaton2._states_number + st2

        def intersect_states(states1, states2):
            return set(state_to_num(st1, st2) for st1, st2 in product(states1, states2))

        instance._states_to_num = {
            State((st1[0], st2[0])): state_to_num(st1[1], st2[1])
            for st1, st2 in product(
                automaton1._states_to_num.items(), automaton2._states_to_num.items()
            )
        }

        instance._start_states = intersect_states(
            automaton1._start_states, automaton2._start_states
        )
        instance._final_states = intersect_states(
            automaton1._final_states, automaton2._final_states
        )
        instance._states_number = automaton1._states_number * automaton2._states_number
        return instance

    @property
    def states_number(self):
        return self._states_number

    @property
    def start_states(self):
        return self._start_states

    @property
    def final_states(self):
        return self._final_states

    @property
    def states_to_num(self):
        return self._states_to_num

    @property
    def adj_matrices(self):
        return self._adj_matrices


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    return AdjacencyMatrixFA.from_intersect(automaton1, automaton2)


def tensor_based_rpq(
    regex: str,
    graph: MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
    matrix_type=sp.csr_matrix,
) -> set[tuple[int, int]]:
    regex_dfa = regex_to_dfa(regex)
    adj_regex = AdjacencyMatrixFA(regex_dfa, matrix_type=matrix_type)
    graph_nfa = graph_to_nfa(graph, start_nodes, final_nodes)
    adj_graph = AdjacencyMatrixFA(graph_nfa, matrix_type=matrix_type)
    adj_intersect = AdjacencyMatrixFA.from_intersect(
        adj_graph, adj_regex, matrix_type=matrix_type
    )

    adj_closure = adj_intersect.transitive_closure()

    def get_state(st1, st2):
        return adj_intersect.states_to_num[State((st1, st2))]

    if adj_intersect.is_empty():
        result = set()
    else:
        result = set(
            state_pair
            for dfa_states_pair in product(
                regex_dfa.start_states, regex_dfa.final_states
            )
            for state_pair in product(graph_nfa.start_states, graph_nfa.final_states)
            if adj_closure[
                get_state(state_pair[0], dfa_states_pair[0]),
                get_state(state_pair[1], dfa_states_pair[1]),
            ]
        )

    if adj_intersect.accepts([]):
        result = result.union(
            set(
                i
                for i in product(graph_nfa.start_states, graph_nfa.final_states)
                if i[0] == i[1]
            )
        )

    return result
