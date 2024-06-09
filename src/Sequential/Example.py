from lxml import etree
import time
import hashlib
import random
import json



# Step 1: Generate Unique Schema Paths
def generate_unique_schema_paths(root, current_path=""):
    paths = set()
    for child in root:
        new_path = f"{current_path}/{child.tag}" if current_path else child.tag
        paths.add(new_path)
        paths.update(generate_unique_schema_paths(child, new_path))
    return paths



# Parse the XML file using lxml
parser = etree.XMLParser(load_dtd=True, dtd_validation=True)
tree = etree.parse('../../data/test.xml', parser)
root = tree.getroot()

# Generate all unique paths
schema_paths = generate_unique_schema_paths(root)
paths = [x for x in schema_paths if 'inproceedings' in x]
print("All Unique Paths:", paths)


start = time.time()

def generate_cover_ranges(query_templates):
    cover_ranges = {"inproceedings": {"inproceedings"}}
    for qt in query_templates:
        parts = qt.split('/')
        key = '/'.join(parts)
        cover_ranges[key] = set()

        base_path = ""
        for part in parts:
            if '[' in part and ']' in part:
                base = part[:part.index('[')]
                conditions = part[part.index('[') + 1:part.index(']')].split(',')
                for condition in conditions:
                    cover_ranges[key].add(f"{base}/{condition.strip()}")
                base_path = f"{base}"
            else:
                base_path = f"{base_path}/{part}"
                cover_ranges[key].add(base_path)
    return cover_ranges


# Example query templates
query_templates = [
    "inproceedings[title]/author",
    "inproceedings[author]",
    "inproceedings[conference]/title"
]

cover_ranges = generate_cover_ranges(query_templates)
print("Cover Ranges:", cover_ranges)



def gamma_related(q1, q2, gamma):
    common_paths = set(q1) & set(q2)
    if common_paths:
        return len(common_paths) / max(len(q1), len(q2)) <= gamma
    return False


def find_gamma_closure(cover_ranges, gamma):
    closures = []
    for qt, paths in cover_ranges.items():
        related_qts = [qt]
        for other_qt, other_paths in cover_ranges.items():
            if other_qt != qt and gamma_related(paths, other_paths, gamma):
                related_qts.append(other_qt)
        closure = set()
        for related_qt in related_qts:
            closure.update(cover_ranges[related_qt])
        closures.append(closure)
    return closures



# gamma = 0.05
# gamma_closures = find_gamma_closure(cover_ranges, gamma)
# print("Gamma Closures:", gamma_closures)


# Step 3: Determine Minimum Determinants
def find_minimum_determinants(paths, fds):
    min_determinants = {}
    for path in paths:
        determinants = None
        for fd in fds:
            if fd[1] == path:
                determinants = fd[0]
        if determinants:
            min_determinants[path] = determinants
        else:
            min_determinants[path] = None
    return min_determinants


fds = [
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings"),
    (["inproceedings/ee", "inproceedings/url"], "inproceedings/title"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/author"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/conference"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/year"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/month"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/crossref"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/pages"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/note"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/cdrom"),
    (["inproceedings/title", "inproceedings/ee"], "inproceedings/url"),
    (["inproceedings/title", "inproceedings/ee", "inproceedings/url"], "inproceedings/booktitle"),
    (["inproceedings/title", "inproceedings/url"], "inproceedings/ee")
]

# fds = [
#     ("inproceedings/title", "inproceedings"),
#     ("inproceedings", "inproceedings/title"),
#     ("inproceedings", "inproceedings/conference"),
#     ("inproceedings", "inproceedings/year"),
#     ("inproceedings", "inproceedings/month"),
#     ("inproceedings", "inproceedings/crossref"),
#     ("inproceedings", "inproceedings/pages"),
#     ("inproceedings", "inproceedings/note"),
#     ("inproceedings", "inproceedings/cdrom"),
#     ("inproceedings", "inproceedings/url"),
#     ("inproceedings", "inproceedings/booktitle"),
#     ("inproceedings", "inproceedings/ee"),
#     ("inproceedings/url", "inproceedings"),
#     ("inproceedings/ee", "inproceedings")
# ]


min_determinants = find_minimum_determinants(paths, fds)
print("Minimum Determinants:", min_determinants)

# Step 4: Create Identifiers
def create_identifiers(paths, cover_ranges, min_determinants, gamma_closures):
    identifiers = {}

    for path in paths:
        if not any(path in cover for cover in cover_ranges.values()):
            identifiers[path] = None
        elif min_determinants[path] is None:
            identifiers[path] = path
        else:
            min_determinant = min_determinants[path]
            if any(any(det in cover for det in min_determinant) for cover in cover_ranges.values()):
            # if any(path in closure and min_determinant in closure for closure in gamma_closures):
                identifiers[path] = min_determinant
            else:
                identifiers[path] = path
    return identifiers


identifiers = create_identifiers(paths, cover_ranges, min_determinants, None)
print("Identifiers:", identifiers)

import hashlib
from lxml import etree


def embed_watermark(root, identifiers, watermark, phi, k):
    def hash_function(i, node_id, k):
        h = hashlib.sha256()
        h.update(f"{i}{node_id}{k}".encode('utf-8'))
        return int(h.hexdigest(), 16)

    watermark_bits = [int(bit) for bit in bin(int(hashlib.sha256(watermark.encode('utf-8')).hexdigest(), 16))[2:]]
    num_bits = len(watermark_bits)

    selected_nodes = []
    for path, node_id in identifiers.items():
        if node_id is not None and "inproceedings" in path and "author" in path:
            nodes = root.xpath(path)
            for node in nodes:
                for i in range(len(node)):
                    r = hash_function(i, node_id, k) % (phi * 100)
                    if r < (phi * 100):
                        j = hash_function(i, node_id, k) % num_bits
                        selected_nodes.append((node, watermark_bits[j]))

    for node, bit in selected_nodes:
        if bit == 0 and len(node):
            node.remove(node[-1])
            print(node)

    return root



def extract_watermark_bits(root, identifiers, phi, k):
    def hash_function(i, node_id, k):
        h = hashlib.sha256()
        h.update(f"{i}{node_id}{k}".encode('utf-8'))
        return int(h.hexdigest(), 16)

    extracted_bits = []
    num_bits = len(bin(int(hashlib.sha256('watermark_text'.encode('utf-8')).hexdigest(), 16))[2:])

    for path, node_id in identifiers.items():
        if node_id is not None:
            nodes = root.xpath(path)
            if nodes:
                for node in nodes:
                    for i in range(len(node.text or '')):
                        r = hash_function(i, node_id, k) % (phi * 100)
                        if r < (phi * 100):
                            j = hash_function(i, node_id, k) % num_bits
                            extracted_bits.append((j, int(node.text[i])))

    return extracted_bits


def reconstruct_watermark(extracted_bits, num_bits):
    watermark_bits = [0] * num_bits
    for index, bit in extracted_bits:
        watermark_bits[index] = bit

    watermark = ''.join(map(str, watermark_bits))
    return watermark


# Usage example
phi = 0.05
k = 'secret_key'
watermark = 'watermark_text'

# Embed the watermark
watermarked_tree = embed_watermark(root, identifiers, watermark, phi, k)
#etree.dump(watermarked_tree)

#extracted_bits = extract_watermark_bits(root, identifiers, phi, k)
#print("Extracted Bits:", extracted_bits)

# Example usage
num_bits = len(bin(int(hashlib.sha256('watermark_text'.encode('utf-8')).hexdigest(), 16))[2:])
#watermark = reconstruct_watermark(extracted_bits, num_bits)
#print("Reconstructed Watermark:", watermark)

print("--- %s seconds ---" % (time.time() - start))