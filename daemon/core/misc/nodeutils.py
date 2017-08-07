"""
Serves as a global point for storing and retrieving node types needed during simulation.
"""

import pprint

from core import logger

_NODE_MAP = None


def _convert_map(x, y):
    """
    Convenience method to create a human readable version of the node map to log.

    :param dict x: dictionary to reduce node items into
    :param tuple y: current node item
    :return:
    """
    x[y[0].name] = y[1]
    return x


def set_node_map(node_map):
    """
    Set the global node map that proides a consistent way to retrieve differently configured nodes.

    :param dict node_map: node map to set to
    :return: nothing
    """
    global _NODE_MAP
    print_map = reduce(lambda x, y: _convert_map(x, y), node_map.items(), {})
    logger.info("setting node class map: \n%s", pprint.pformat(print_map, indent=4))
    _NODE_MAP = node_map


def get_node_class(node_type):
    """
    Retrieve the node class for a given node type.

    :param int node_type: node type to retrieve class for
    :return: node class
    """
    global _NODE_MAP
    return _NODE_MAP[node_type]


def is_node(obj, node_types):
    """
    Validates if an object is one of the provided node types.

    :param obj: object to check type for
    :param int|tuple|list node_types: node type(s) to check against
    :return: True if the object is one of the node types, False otherwise
    :rtype: bool
    """
    type_classes = []
    if isinstance(node_types, (tuple, list)):
        for node_type in node_types:
            type_class = get_node_class(node_type)
            type_classes.append(type_class)
    else:
        type_class = get_node_class(node_types)
        type_classes.append(type_class)

    return isinstance(obj, tuple(type_classes))
