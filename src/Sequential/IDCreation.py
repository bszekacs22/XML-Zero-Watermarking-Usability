from lxml import etree


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
print("All Unique Paths:", schema_paths)


# Step 2: Generate Cover Ranges and Gamma Closures
def generate_cover_ranges(query_templates):
    cover_ranges = {}
    for qt in query_templates:
        parts = qt.split('/')
        cover_ranges[qt] = set()
        for i in range(1, len(parts)):
            cover_ranges[qt].add('/'.join(parts[:i]))
            if '[' in parts[i] and ']' in parts[i]:
                conditions = parts[i][parts[i].index('[')+1:parts[i].index(']')].split(',')
                for condition in conditions:
                    cover_ranges[qt].add('/'.join(parts[:i]) + '/' + condition.strip())
    return cover_ranges



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


query_templates = [
    "Root/inproceedings[title]/author",
    "Root/inproceedings[title]/journal"
]

cover_ranges = generate_cover_ranges(query_templates)
print("Cover Ranges:", cover_ranges)

gamma = 0.05
gamma_closures = find_gamma_closure(cover_ranges, gamma)
print("Gamma Closures:", gamma_closures)


# Step 3: Determine Minimum Determinants
def find_minimum_determinants(schema_paths, fds):
    min_determinants = {}
    for path in schema_paths:
        determinants = [fd[0] for fd in fds if fd[1] == path]
        if determinants:
            min_determinants[path] = min(determinants, key=len)
        else:
            min_determinants[path] = None
    return min_determinants


fds = [
    ("Root/inproceedings/title", "Root/inproceedings"),
    ("Root/inproceedings/author", "Root/inproceedings")
]
min_determinants = find_minimum_determinants(schema_paths, fds)
print("Minimum Determinants:", min_determinants)


# Step 4: Create Identifiers
def create_identifiers(schema_paths, cover_ranges, min_determinants, gamma_closures):
    identifiers = {}

    for path in schema_paths:
        if not any(path in cover for cover in cover_ranges.values()):
            identifiers[path] = None
        elif min_determinants[path] is None:
            longest_prefix = "/".join(path.split("/")[:-1])
            if longest_prefix in identifiers:
                identifiers[path] = identifiers[longest_prefix] + "/" + path.split("/")[-1]
            else:
                identifiers[path] = path
        else:
            min_determinant = min_determinants[path]
            if any(path in closure and min_determinant in closure for closure in gamma_closures):
                identifiers[path] = min_determinant
            else:
                identifiers[path] = path

    return identifiers


identifiers = create_identifiers(schema_paths, cover_ranges, min_determinants, gamma_closures)
print("Identifiers:", identifiers)
