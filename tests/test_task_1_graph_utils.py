from project.task_1_graph_utils import *
import shutil
import os


class TestGetGraphData:
    def test_graph_data_skos(self):
        graph_name = 'skos'
        labels = ['type', 'definition', 'isDefinedBy', 'label', 'subPropertyOf', 'comment', 'scopeNote', 'inverseOf',
                  'range', 'domain', 'contributor', 'disjointWith', 'creator', 'example', 'first', 'rest',
                  'description', 'seeAlso', 'subClassOf', 'title', 'unionOf']
        expected_graph_data = GraphData(144, 252, labels)
        assert get_graph_data(graph_name) == expected_graph_data

    def test_graph_data_gzip(self):
        graph_name = 'foaf'
        labels = ['type', 'label', 'comment', 'term_status', 'isDefinedBy', 'domain', 'range', 'subPropertyOf',
                  'subClassOf', 'disjointWith', 'inverseOf', 'equivalentClass', 'description', 'equivalentProperty',
                  'title']
        expected_graph_data = GraphData(256, 631, labels)
        assert get_graph_data(graph_name) == expected_graph_data


class TestCycledGraphCreater:
    # teardown removes all files in this directory
    results_path = "test_data"

    def get_graph_path(self, graph_name) -> str:
        return os.path.join(self.results_path, graph_name + ".dot")

    def test_graph_data_my_graph(self):
        expected = """digraph  {
1;
2;
3;
4;
5;
0;
6;
7;
1 -> 2 [key=0, label=Hello];
2 -> 3 [key=0, label=Hello];
3 -> 4 [key=0, label=Hello];
4 -> 5 [key=0, label=Hello];
5 -> 0 [key=0, label=Hello];
0 -> 1 [key=0, label=Hello];
0 -> 6 [key=0, label=world];
6 -> 7 [key=0, label=world];
7 -> 0 [key=0, label=world];
}
"""
        graph_path = self.get_graph_path("my_graph")
        create_and_save_graph(5, 2, ("Hello", "world"), graph_path)
        with open(graph_path, "r") as f:
            assert f.read() == expected


    @classmethod
    def setup_class(cls):
        os.mkdir(cls.results_path)


    @classmethod
    def teardown_class(cls):
        pass
        shutil.rmtree(cls.results_path)
