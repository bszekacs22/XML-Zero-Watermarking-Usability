
import lxml.etree as ET
import os
import generate
import usability_generate as ugenerate
import matplotlib.pyplot as plt
import numpy as np


def specific_attribute_attack(root, tree, tag_to_remove):
    for elem in list(root):
        children_to_remove = [child for child in elem if child.tag == tag_to_remove]
        for child in children_to_remove:
            elem.remove(child)

    # Save the modified XML to a new file
    new_xml_file = f"../../data/modified_{os.path.basename(xml_file)}"
    tree.write(new_xml_file, encoding='utf-8', xml_declaration=True)

    return new_xml_file


# Function to simulate specific attribute attack and run detection
def simulate_specific_attribute_attack(file_path,
                                       tag_to_remove):
    # Reload the XML tree
    root, tree = parse_xml(file_path)

    # Generate a secret key and IV (store these securely)
    secret_key = generate.generate_key()
    iv = generate.generate_iv()

    # Generate the watermark
    original_watermark = generate.generate_watermark(xml_file, secret_key, iv)
    usability_watermark = ugenerate.generate_watermark(xml_file, secret_key, iv)

    # Perform the specific attribute attack
    attacked_xml_file = specific_attribute_attack(root, tree, tag_to_remove)

    # Run watermark detection
    sim1 = generate.detect_watermark(attacked_xml_file, secret_key, iv, original_watermark)
    sim2 = ugenerate.detect_watermark(attacked_xml_file, secret_key, iv, usability_watermark)

    return sim1, sim2


# Function to parse XML and reload the tree
def parse_xml(file_path):
    parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
    tree = ET.parse(file_path, parser)
    root = tree.getroot()
    return root, tree


def generate_cover_ranges(query_templates):
    attribute_set = set()
    for qt in query_templates:
        parts = qt.split('/')
        for part in parts:
            if '[' in part and ']' in part:
                conditions = part[part.index('[') + 1:part.index(']')].split(',')
                for condition in conditions:
                    attribute_set.add(condition.strip())
            else:
                if part:
                    attribute_set.add(part)
    return attribute_set




# Function to plot the results
def plot_similarity_histogram(results):
    tags = list(results.keys())
    sim1_values = [results[tag][0] for tag in tags]
    sim2_values = [results[tag][1] for tag in tags]

    x = np.arange(len(tags))

    plt.figure(figsize=(10, 6))

    bar_width = 0.35  # Adjust bar width

    plt.bar(x - bar_width/2, sim1_values, width=bar_width, label='Original Algorithm', align='center')
    plt.bar(x + bar_width/2, sim2_values, width=bar_width, label='Improved Algorithm', align='center')

    plt.xlabel('Tags')
    plt.ylabel('Similarity')
    plt.title('Similarity After Specific Attribute Attack')
    plt.xticks(x, tags)
    plt.legend()
    plt.grid(True)

    plt.savefig('similarity_histogram.png')
    plt.show()



xml_file = '../../data/dblp_small.xml'

query_templates = [
    "inproceedings[title]/author",
    "inproceedings[author]",
    "inproceedings[conference]/title",
    "inproceedings[year]/title",
    "inproceedings[title]/booktitle"
]


# Sample usage with your parameters
tags_to_remove = ['crossref', 'ee', 'pages', 'url', 'booktitle', 'conference', 'year']  # List of tags to remove in separate runs


results = {}
for tag in tags_to_remove:
    sim1, sim2 = simulate_specific_attribute_attack(xml_file, tag)
    results[tag] = (sim1, sim2)


# Call the function to plot the histogram
plot_similarity_histogram(results)
