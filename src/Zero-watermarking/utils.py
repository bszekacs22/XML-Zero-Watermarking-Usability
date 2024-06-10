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
                    if child.text in attribute_partitions[attr].keys():
                        attribute_partitions[attr][child.text] = attribute_partitions[attr][child.text] | {node}
                    else: attribute_partitions[attr][child.text] = {node}
                else:
                    attribute_partitions[attr] = {child.text: {node}}

    return attribute_partitions

def combine_attribute_partitions(key1, key2, parts):
    combinedkey = key1 | key2
    for k1 in parts[key1]:
        for k2 in parts[key2]:
            e1 = parts[key1][k1]
            e2 = parts[key2][k2]
            elems = e1 & e2
            if elems:
                parts[combinedkey][frozenset({k1}) | frozenset({k2})] = elems
    return parts

