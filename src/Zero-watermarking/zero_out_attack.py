import random
import lxml.etree as ET
import os
import generate
import usability_generate as ugenerate
import matplotlib.pyplot as plt
import numpy as np



def random_zero_out_attack(root, tree, rate):
    # Get all elements in the XML tree
    nodes = list(root)
    num_to_remove = int(len(nodes) * rate)

    # Randomly select elements to attack
    elements_to_attack = random.sample(nodes, num_to_remove)

    # Zero out the attributes of the selected elements
    for elem in elements_to_attack:
        for child in elem:
            child.text = '0'

    # Save the modified XML to a new file
    new_xml_file = f"../../data/modified_{os.path.basename(xml_file)}"
    tree.write(new_xml_file, encoding='utf-8', xml_declaration=True)

    return new_xml_file


def random_zero_out_attribute_attack(root, tree,  rate):
    # Get all child elements in the XML tree
    nodes = list(root)
    all_elements = [child for node in nodes for child in node]

    # Determine the number of child elements to attack based on the rate
    num_elements_to_attack = int(rate * len(all_elements))

    # Randomly select child elements to attack
    elements_to_attack = random.sample(all_elements, num_elements_to_attack)

    # Zero out the text of the selected child elements
    for elem in elements_to_attack:
        elem.text = '0'

    # Save the modified XML to a new file
    new_xml_file = f"../../data/modified_{os.path.basename(xml_file)}"
    tree.write(new_xml_file, encoding='utf-8', xml_declaration=True)

    return new_xml_file


# Function to simulate random zero-out attack and run detection
def simulate_random_zero_out_attack(xml_file, removal_rates):
    results = {}

    # Generate a secret key and IV (store these securely)
    secret_key = generate.generate_key()
    iv = generate.generate_iv()

    # Generate the watermark
    original_watermark = generate.generate_watermark(xml_file, secret_key, iv)
    usability_watermark = ugenerate.generate_watermark(xml_file, secret_key, iv)

    root, tree = parse_xml(xml_file)

    for rate in removal_rates:
        print(f"Simulating random zero-out attack with rate {rate}")

        # Perform the random zero-out attack
        attacked_xml_file = random_zero_out_attack(root, tree, rate)

        # Run watermark detection
        sim1 = generate.detect_watermark(attacked_xml_file, secret_key, iv, original_watermark)
        sim2 = ugenerate.detect_watermark(attacked_xml_file, secret_key, iv, usability_watermark)

        results[rate] = (sim1, sim2)
    return results


# Function to parse XML and reload the tree
def parse_xml(file_path):
    parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
    tree = ET.parse(file_path, parser)
    root = tree.getroot()
    return root, tree

def plot_similarity_over_attack_rate(average_results):
    rates = sorted(average_results.keys())
    sim1_values = [average_results[rate][0] for rate in rates]
    sim2_values = [average_results[rate][1] for rate in rates]

    plt.figure(figsize=(10, 6))

    plt.plot(rates, sim1_values, label='Original Algorithm', marker='o')
    plt.plot(rates, sim2_values, label='Usability Algorithm', marker='x')

    plt.xlabel('Zero-Out Rate')
    plt.ylabel('Similarity')
    plt.title('Similarity Over Zero-Out Rate')
    plt.legend()
    plt.grid(True)

    plt.savefig('similarity_over_zeroout_rate.png')
    plt.show()



# Sample usage with your parameters
removal_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
num_runs = 5

xml_file = '../../data/dblp_small.xml'  # Replace with your XML file path

# Collect results from multiple runs
all_results = []
for i in range(num_runs):
    results = simulate_random_zero_out_attack(xml_file, removal_rates)
    all_results.append(results)

# Average the results
average_results = {rate: (np.mean([run[rate][0] for run in all_results]), np.mean([run[rate][1] for run in all_results])) for rate in removal_rates}

# Function to plot the results

# Call the function to plot the graph
plot_similarity_over_attack_rate(average_results)