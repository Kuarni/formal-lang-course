from project.task_1_graph_utils import GraphData, get_graph_data, create_and_save_graph
import shutil
import os


class TestGetGraphData:
    def test_graph_data_skos(self):
        graph_name = "skos"
        labels = [
            "type",
            "definition",
            "isDefinedBy",
            "label",
            "subPropertyOf",
            "comment",
            "scopeNote",
            "inverseOf",
            "range",
            "domain",
            "contributor",
            "disjointWith",
            "creator",
            "example",
            "first",
            "rest",
            "description",
            "seeAlso",
            "subClassOf",
            "title",
            "unionOf",
        ]
        expected_graph_data = GraphData(144, 252, labels)
        assert get_graph_data(graph_name) == expected_graph_data

    def test_graph_data_gzip(self):
        graph_name = "foaf"
        labels = [
            "type",
            "label",
            "comment",
            "term_status",
            "isDefinedBy",
            "domain",
            "range",
            "subPropertyOf",
            "subClassOf",
            "disjointWith",
            "inverseOf",
            "equivalentClass",
            "description",
            "equivalentProperty",
            "title",
        ]
        expected_graph_data = GraphData(256, 631, labels)
        assert get_graph_data(graph_name) == expected_graph_data


class TestCycledGraphCreater:
    # teardown removes all files in this directory
    results_path = "test_data"

    def get_graph_path(self, graph_name) -> str:
        return os.path.join(self.results_path, graph_name + ".dot")

    def test_graph_data_my_graph(self):
        reference_path = "task_1_reference_graph.dot"

        graph_path = self.get_graph_path("my_graph")
        create_and_save_graph(5, 2, ("Hello", "world"), graph_path)
        with open(graph_path, "r") as f:
            with open(reference_path, "r") as reference:
                assert f.read() == reference.read()

    @classmethod
    def setup_class(cls):
        os.mkdir(cls.results_path)

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.results_path)
