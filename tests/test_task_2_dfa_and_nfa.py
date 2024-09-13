from collections.abc import Iterable
from pyformlang.finite_automaton import Symbol

from project.task_2_dfa_and_nfa import regex_to_dfa


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
