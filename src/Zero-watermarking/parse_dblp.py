import time
from lxml import etree
from collections import defaultdict


def generate_attribute_partitions_iter(xml_file, tag='inproceedings', limit=None):
    start_time = time.time()

    # Set up the iterparse context with DTD validation using lxml.etree
    context = etree.iterparse(xml_file, events=("start", "end"), load_dtd=True, dtd_validation=True)
    attribute_partitions = defaultdict(lambda: defaultdict(set))

    count = 0

    for event, elem in context:
        if event == "end" and elem.tag == tag:
            count += 1
            for child in elem:
                if child.text and child.text.strip():
                    attr = child.tag
                    value = child.text.strip()
                elif child.attrib:
                    attr = child.tag
                    value = tuple(child.attrib.items())
                else:
                    continue

                attribute_partitions[frozenset({attr})][value].add(etree.tostring(elem, encoding='unicode'))
            elem.clear()

            # Stop parsing if limit is reached
            if limit is not None and count >= limit:
                break

    end_time = time.time()
    print(f"Time taken to parse and process {count} {tag} elements: {end_time - start_time:.2f} seconds")

    return attribute_partitions


# Example usage
xml_file = '../../data/dblp-2015.xml'

# Limit to processing the first 1000 'inproceedings' elements
attribute_partitions = generate_attribute_partitions_iter(xml_file)
#print("Attribute Partitions:", attribute_partitions)
