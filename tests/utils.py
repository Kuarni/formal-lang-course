from pathlib import Path
from typing import Iterable

from pyformlang.finite_automaton import Symbol


def get_path_in_same_dir(path_to_python_file: str, name_of_file_for_path: str) -> Path:
    return Path(path_to_python_file).parent.joinpath(name_of_file_for_path)


def str2symbols(string: str) -> Iterable[Symbol]:
    return [Symbol(char) for char in string]
