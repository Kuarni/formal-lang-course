from project.task3 import AdjacencyMatrixFA
from project.task2 import regex_to_dfa
from utils import str2symbols


class TestAdjacencyMatrixFA:
    def test_simple_regex(self):
        dfa = regex_to_dfa("a.(a|b)*")
        adj_fa = AdjacencyMatrixFA(dfa)
        assert not adj_fa.is_empty()
        assert adj_fa.accepts(str2symbols("a"))
        assert adj_fa.accepts(str2symbols("ab"))
        assert adj_fa.accepts(str2symbols("aa"))
        assert adj_fa.accepts(str2symbols("aaba"))
        assert not adj_fa.accepts(str2symbols("ba"))
        assert not adj_fa.accepts([])

    def test_empty_regex(self):
        dfa = regex_to_dfa("")
        adj_matrix = AdjacencyMatrixFA(dfa)
        assert adj_matrix.is_empty()
        assert not adj_matrix.accepts(str2symbols("a"))

    def test_intersection(self):
        dfa1 = AdjacencyMatrixFA(regex_to_dfa("a b c*"))
        dfa2 = AdjacencyMatrixFA(regex_to_dfa("(a | b | c)*(d | e | f)*"))
        adj_matrix = AdjacencyMatrixFA.from_intersect(dfa1, dfa2)
        assert not adj_matrix.is_empty()
        assert adj_matrix.accepts(str2symbols("abcc"))
        assert not adj_matrix.accepts(str2symbols("def"))
