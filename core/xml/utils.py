from xml.etree import ElementTree
from xml.dom import minidom


def get_pretty_xml(tree):
    """Transforms and pretty-prints a given xml-tree to string

    :param tree: XML-tree
    :type tree: object
    :returns: (Prettified) stringified version of the passed xml-tree
    :rtype: str
    """
    stringified_tree = ElementTree.tostring(tree.getroot(), 'utf-8')
    minidoc = minidom.parseString(stringified_tree)
    return minidoc.toprettyxml(indent="  ")
