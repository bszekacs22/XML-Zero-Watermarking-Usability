from lxml import etree
import time



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

def generate_node_ids(root, path_identifiers):
    node_ids = {}

    for path, path_id in path_identifiers.items():
        if path_id is not None:
            nodes = root.xpath(path)
            for index, node in enumerate(nodes):
                node_id = create_node_id(path, node)
                node_ids[(path, index)] = node_id

    return node_ids

def create_node_id(path, node):
    # Collect node attributes and text content to form a unique query
    attribute_conditions = []
    for attr, value in node.attrib.items():
        attribute_conditions.append(f'@{attr}="{value}"')

    # Add the node text if it exists
    if node.text and node.text.strip():
        attribute_conditions.append(f'text()="{node.text.strip()}"')

    # Combine the path and conditions to form the node identifier
    conditions = " and ".join(attribute_conditions)
    node_id = f'{path}[{conditions}]' if conditions else path

    return node_id


identifiers = create_identifiers(paths, cover_ranges, min_determinants, None)
print("Identifiers:", identifiers)

node_ids = generate_node_ids(root, identifiers)
print("Node Identifiers:", node_ids)

print("--- %s seconds ---" % (time.time() - start))