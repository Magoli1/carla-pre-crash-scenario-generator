from xml.etree import ElementTree
from xml.dom import minidom

def get_pretty_xml(tree):
    stringified_tree = ElementTree.tostring(tree.getroot(), 'utf-8')
    minidoc = minidom.parseString(stringified_tree)
    return minidoc.toprettyxml(indent="  ")
