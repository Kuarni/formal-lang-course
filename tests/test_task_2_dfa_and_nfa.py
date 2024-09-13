import os
import shutil
import networkx as nx
from collections.abc import Iterable
from pyformlang.finite_automaton import Symbol, NondeterministicFiniteAutomaton, State

from project.task_1_graph_utils import get_graph, create_and_save_graph
from project.task_2_dfa_and_nfa import regex_to_dfa, graph_to_nfa


class TestRegexToDfa:
    @staticmethod
    def str2symbols(string: str) -> Iterable[Symbol]:
        return [Symbol(char) for char in string]

    def test_empty_regex(self):
        dfa = regex_to_dfa("")
        assert dfa.is_deterministic()
        assert dfa.is_empty()

    def test_simple_regex(self):
        dfa = regex_to_dfa("a")
        assert dfa.is_deterministic()
        assert dfa.accepts(self.str2symbols("a"))
        assert not dfa.accepts(self.str2symbols("b"))
        assert not dfa.accepts(self.str2symbols("ab"))

    def test_concat_symbols(self):
        dfa = regex_to_dfa("a b.o.b a")
        assert dfa.accepts(self.str2symbols("aboba"))
        assert not dfa.accepts(self.str2symbols("aboba "))
        assert not dfa.accepts(self.str2symbols("abob"))

    def test_union(self):
        dfa = regex_to_dfa("a|b+c")
        assert dfa.accepts(self.str2symbols("a"))
        assert dfa.accepts(self.str2symbols("b"))
        assert dfa.accepts(self.str2symbols("c"))
        assert not dfa.accepts(self.str2symbols("bbc"))

    def test_kleene(self):
        dfa = regex_to_dfa("a*b*")
        assert dfa.accepts(self.str2symbols(""))
        assert dfa.accepts(self.str2symbols("aaaa"))
        assert dfa.accepts(self.str2symbols("bbbb"))
        assert dfa.accepts(self.str2symbols("aaaabbb"))
        assert not dfa.accepts(self.str2symbols("ba"))

    def test_groups(self):
        dfa = regex_to_dfa("(b.a)*")
        assert dfa.accepts(self.str2symbols(""))
        assert dfa.accepts(self.str2symbols("ba"))
        assert dfa.accepts(self.str2symbols("baba"))
        assert not dfa.accepts(self.str2symbols("aaa"))

    def test_epsilon(self):
        dfa = regex_to_dfa("(a|epsilon) (c|$)")
        assert dfa.accepts(self.str2symbols("ac"))
        assert dfa.accepts(self.str2symbols("a"))
        assert dfa.accepts(self.str2symbols("c"))
        assert dfa.accepts(self.str2symbols(""))
        assert not dfa.accepts(self.str2symbols("b"))
        assert not dfa.accepts(self.str2symbols("ac "))

    def test_escaped(self):
        dfa = regex_to_dfa("\\*")
        assert dfa.accepts(self.str2symbols("*"))

    def test_big_symbol(self):
        dfa = regex_to_dfa("ab c")
        assert dfa.accepts([Symbol("ab"), Symbol("c")])
        assert not dfa.accepts(self.str2symbols("abc"))

    def test_is_minimum(self):
        dfa = regex_to_dfa("i*.s (m.i)|(n.i)+m.u.m.$")
        min_dfa = dfa.minimize()
        assert dfa == min_dfa


class TestGraphToNfa:
    # teardown removes all files in this directory
    results_path = "test_2_data"

    def get_graph_path(self, graph_name) -> str:
        return os.path.join(self.results_path, graph_name + ".dot")

    def test_is_nfa(self):
        graph = get_graph("skos")
        nfa = graph_to_nfa(graph)
        assert not nfa.is_deterministic()

    @staticmethod
    def get_expected_nfa_for_tests(start_states, final_states):
        expected_nfa = NondeterministicFiniteAutomaton()
        for i in start_states:
            expected_nfa.add_start_state(State(i))
        for i in final_states:
            expected_nfa.add_final_state(State(i))

        expected_nfa.add_transition(State(1), Symbol("a"), State(0))
        expected_nfa.add_transition(State(0), Symbol("a"), State(1))
        expected_nfa.add_transition(State(2), Symbol("b"), State(0))
        expected_nfa.add_transition(State(0), Symbol("b"), State(2))
        return expected_nfa

    def test_nfa_no_final_start_state(self):
        graph_path = self.get_graph_path("graph_1")
        create_and_save_graph(1, 1, ("a", "b"), graph_path)

        graph = nx.drawing.nx_pydot.read_dot(graph_path)
        nfa = graph_to_nfa(graph)

        assert len(nfa.start_states) == len(nfa.states)
        assert len(nfa.final_states) == len(nfa.states)

        expected_nfa = self.get_expected_nfa_for_tests({0, 1, 2}, {0, 1, 2})
        assert nfa.is_equivalent_to(expected_nfa)

    def test_nfa_with_final_start_states(self):
        graph_path = self.get_graph_path("graph_2")
        create_and_save_graph(1, 1, ("a", "b"), graph_path)

        graph = nx.drawing.nx_pydot.read_dot(graph_path)
        nfa = graph_to_nfa(graph, {1}, {2})

        assert len(nfa.start_states) == 1
        assert len(nfa.final_states) == 1

        expected_nfa = self.get_expected_nfa_for_tests({1}, {2})
        assert nfa.is_equivalent_to(expected_nfa)

    def test_nfa_with_several_start_states(self):
        graph_path = self.get_graph_path("graph_3")
        create_and_save_graph(1, 1, ("a", "b"), graph_path)

        graph = nx.drawing.nx_pydot.read_dot(graph_path)
        nfa = graph_to_nfa(graph, {1, 0}, {2})

        assert len(nfa.start_states) == 2
        assert len(nfa.final_states) == 1

        expected_nfa = self.get_expected_nfa_for_tests({1, 0}, {2})
        assert nfa.is_equivalent_to(expected_nfa)

    def setup_class(self):
        os.mkdir(self.results_path)

    def teardown_class(self):
        shutil.rmtree(self.results_path)
