from typing import Set
from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    regex = Regex(regex)
    return regex.to_epsilon_nfa().to_deterministic().minimize()


def graph_to_nfa(
    graph: MultiDiGraph, start_states: Set[int] = None, final_states: Set[int] = None
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    start_states_ = [i for i in start_states] if start_states else nfa.states
    final_states_ = [i for i in final_states] if final_states else nfa.states

    for i in start_states_:
        nfa.add_start_state(i)
    for i in final_states_:
        nfa.add_final_state(i)
    return nfa
