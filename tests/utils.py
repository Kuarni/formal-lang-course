from pathlib import Path


def get_path_in_same_dir(path_to_python_file: str, name_of_file_for_path: str) -> Path:
    return Path(path_to_python_file).parent.joinpath(name_of_file_for_path)
