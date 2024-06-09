from lxml import etree
import pandas as pd
from itertools import combinations

# Step 1: Parse XML and Extract Data
def parse_xml_to_dataframe(root):
    data = []

    for elem in root:
        record = {}
        for child in elem:
            if child.tag in record:
                if isinstance(record[child.tag], list):
                    record[child.tag].append(child.text)
                else:
                    record[child.tag] = [record[child.tag], child.text]
            else:
                record[child.tag] = child.text
        data.append(record)

    df = pd.DataFrame(data)
    return df.applymap(lambda x: '|'.join(x) if isinstance(x, list) else x)

# Step 2: Generate Initial FDs
def generate_initial_fds(attributes):
    initial_fds = []
    for lhs in attributes:
        for rhs in attributes:
            if lhs != rhs:
                initial_fds.append(([lhs], rhs))
    return initial_fds

# Step 3: Prune Non-minimal FDs
def closure(attributes, fds):
    closure_set = set(attributes)
    while True:
        new_attributes = set(a for lhs, rhs in fds if set(lhs).issubset(closure_set) for a in rhs)
        if new_attributes.issubset(closure_set):
            break
        closure_set.update(new_attributes)
    return closure_set

def prune_non_minimal_fds(fds):
    pruned_fds = fds[:]
    for lhs, rhs in fds:
        lhs_closure = closure(lhs, fds)
        for attr in rhs:
            if attr not in lhs_closure:
                pruned_fds.append((lhs, [attr]))
    return pruned_fds

# Step 4: Validate FDs
def validate_fds(df, fds):
    valid_fds = []
    for lhs, rhs in fds:
        lhs_values = df[list(lhs)].drop_duplicates().values
        rhs_values = df[lhs + rhs].drop_duplicates().values
        if len(lhs_values) == len(rhs_values):
            valid_fds.append((lhs, rhs))
    return valid_fds

# Full DiscoverXFD Algorithm
def discover_xfd(xml_file):
    df = parse_xml_to_dataframe(xml_file)
    attributes = df.columns.tolist()
    initial_fds = generate_initial_fds(attributes)
    pruned_fds = prune_non_minimal_fds(initial_fds)
    #valid_fds = validate_fds(df, pruned_fds)
    return pruned_fds


# Example usage
xml_file = '../../data/test.xml'
parser = etree.XMLParser(load_dtd=True, dtd_validation=True)
tree = etree.parse(xml_file, parser)
xml_root = tree.getroot()
fds = discover_xfd(xml_root)

print("Discovered Functional Dependencies:")
for lhs, rhs in fds:
    print(f"{lhs} -> {rhs}")
