from xml.etree.ElementTree import Element, ElementTree


def initialize_xml_tree(root_tag_name="scenarios"):
    """Initializes a new xml-tree with a given root element

    :param root_tag_name: Name of the root tag
    :type root_tag_name: str
    :returns: New xml-tree with root element
    :rtype: object
    """
    root = Element(root_tag_name)
    return ElementTree(root)
