from xml.etree.ElementTree import Element, ElementTree


def initialize_xml_tree():
    root = Element("scenarios")
    return ElementTree(root)
