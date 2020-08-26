from pathlib import Path
import time

from core.xml.utils import get_pretty_xml


def write_xml(tree, filename=None, path="output/", ):
    if filename is None:
        filename = "scenario_output_" + time.strftime("%Y%m%d-%H%M%S") + ".xml"
    if not filename.endswith(".xml"):
        filename += ".xml"
    if not path.endswith("/"):
        path += "/"
    if path.startswith("/"):
        path = path[1:]

    create_output_folder(path)
    write_tree(tree, path, filename)


def write_tree(tree, path, filename):
    path_to_file = path + filename
    pretty_xml = get_pretty_xml(tree)
    with open(path_to_file, "w") as f:
        f.write(pretty_xml)


def create_output_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)
