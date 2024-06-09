from collections import defaultdict



def generate_attribute_partitions(root, tag):
    attribute_partitions = defaultdict(dict)

    # Find all nodes with the specified tag (e.g., 'inproceedings')
    nodes = root.findall(f'.//{tag}')

    for node in nodes:
        # Collect the child elements and their text values for each node
        for child in node:
            attr = frozenset({child.tag})
            if child.text:
                if attr in attribute_partitions.keys():
                    attribute_partitions[attr][child.text] = (node)
                else:
                    attribute_partitions[attr] = {child.text: node}

    return attribute_partitions

