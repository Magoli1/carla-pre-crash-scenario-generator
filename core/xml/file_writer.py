from pathlib import Path
import time
from xml.etree.ElementTree import ElementTree

from core.xml.utils import get_pretty_xml


def write_xml(tree, filename=None, path="../../output/", ):
    if(filename is None):
        filename = "scenario_output_" + time.strftime("%Y%m%d-%H%M%S") + ".xml"
    if(not filename.endswith(".xml")):
        filename += ".xml"
    if(not path.endswith("/")):
        path += "/"
    if(path.startswith("/")):
        path = path[1:]
    current_dir = Path(__file__).parent
    joined_path = (current_dir / path).resolve()
    createOutputFolder(joined_path)
    write_tree(tree, joined_path, filename)


def write_tree(tree, path, filename):
    path_to_file = (path / filename).resolve()
    prettyXML = get_pretty_xml(tree)
    with open(path_to_file, "w") as f:
        f.write(prettyXML)


def createOutputFolder(path):
    Path(path).mkdir(parents=True, exist_ok=True)
