import random
import lxml.etree as ET
import os
import generate
import usability_generate as ugenerate
import matplotlib.pyplot as plt
import numpy as np


def selection_attack(root, tree, rate, tags):
    # Collect all children of the root node
    all_elements = list(root)

    # Determine the number of elements to attack based on the rate
    num_elements_to_attack = int(rate * len(all_elements))

    # Randomly select elements to attack
    elements_to_attack = random.sample(all_elements, num_elements_to_attack)

    # Remove unimportant children of the selected elements
    for elem in elements_to_attack:
        for child in list(elem):
            if child.tag not in tags:
                child.text = '0'

    # Save the modified XML to a new file
    new_xml_file = f"../../data/modified_{os.path.basename(xml_file)}"
    tree.write(new_xml_file, encoding='utf-8', xml_declaration=True)

    return new_xml_file



def simulate_selection_attack(xml_file, rates, tags):
    results = {}

    # Generate a secret key and IV (store these securely)
    secret_key = generate.generate_key()
    iv = generate.generate_iv()

    # Generate the watermark
    original_watermark = generate.generate_watermark(xml_file, secret_key, iv)
    usability_watermark = ugenerate.generate_watermark(xml_file, secret_key, iv)

    root, tree = parse_xml(xml_file)

    for rate in rates:
        print(f"Simulating selection attack with rate {rate}")
        # Perform the selection attack
        attacked_xml_file = selection_attack(root, tree, rate, tags)

        # Run watermark detection
        sim1 = generate.detect_watermark(attacked_xml_file, secret_key, iv, original_watermark)
        sim2 = ugenerate.detect_watermark(attacked_xml_file, secret_key, iv, usability_watermark)

        results[rate] = (sim1, sim2)

    return results


def plot_similarity_over_attack_rate(results):
    rates = sorted(results.keys())
    sim1_values = [results[rate][0] for rate in rates]
    sim2_values = [results[rate][1] for rate in rates]

    plt.figure(figsize=(10, 6))

    plt.plot(rates, sim1_values, label='Original Algorithm', marker='o')
    plt.plot(rates, sim2_values, label='Usability Algorithm', marker='x')

    plt.xlabel('Targeted Zero-Out Rate')
    plt.ylabel('Similarity')
    plt.title('Similarity Over Targeted Zero-Out Rate')
    plt.legend()
    plt.grid(True)

    plt.savefig('similarity_over_targeted_zero_out_rate.png')
    plt.show()


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



xml_file = '../../data/dblp_small.xml'


# Define removal rates to simulate
removal_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
num_runs = 5

query_templates = [
    "inproceedings[title]/author",
    "inproceedings[author]",
    "inproceedings[conference]/title",
    "inproceedings[year]/title",
    "inproceedings[title]/booktitle"
]

tags = generate_cover_ranges(query_templates)

all_results = []
for i in range(num_runs):
    results = simulate_selection_attack(xml_file, removal_rates, tags)
    all_results.append(results)

# Average the results
average_results = {rate: (np.mean([run[rate][0] for run in all_results]), np.mean([run[rate][1] for run in all_results])) for rate in removal_rates}


# Print the results
print("Selection Attack Simulation Results:")
for rate, is_valid in results.items():
    print(f"Rate: {rate}, Watermark Valid: {is_valid}")

# Call the function to plot the graph
plot_similarity_over_attack_rate(results)