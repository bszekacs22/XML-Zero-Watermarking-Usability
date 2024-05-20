from lxml import etree
import hashlib
import random
import json

# Preprocess the XML file to replace undefined entities
def preprocess_xml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace common HTML entities with their equivalent character or remove them
    replacements = {
        '&uuml;': 'ü',
        '&ouml;': 'ö',
        '&auml;': 'ä',
        '&szlig;': 'ß',
        '&amp;': '&',
        '&quot;': '"',
        '&apos;': "'",
        '&lt;': '<',
        '&gt;': '>'
    }

    for entity, char in replacements.items():
        content = content.replace(entity, char)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Preprocess the XML file
# preprocess_xml('../../data/test.xml')

# Parse the XML file using lxml
parser = etree.XMLParser(load_dtd=True, no_network=False)
tree = etree.parse('../../data/test.xml', parser)
root = tree.getroot()

# Extract data
data = []
for article in root.findall('inproceedings'):
    record = {child.tag: child.text for child in article}
    data.append(record)

# Define the identifier creation function
def create_identifier(schema, fds, query_templates, gamma):
    def gamma_related(q1, q2):
        common_paths = set(q1) & set(q2)
        if common_paths:
            return len(common_paths) / max(len(q1), len(q2)) <= gamma
        return False

    def find_gamma_closure(query_templates):
        closures = []
        for qt in query_templates:
            related_qts = [qt]
            for other in query_templates:
                if other != qt and gamma_related(qt, other):
                    related_qts.append(other)
            closures.append(set().union(*related_qts))
        return closures

    gamma_closures = find_gamma_closure(query_templates)
    identifiers = {}
    for path in schema:
        if not any(path in qt for qt in query_templates):
            identifiers[path] = None
        elif not any(fd[1] == path for fd in fds):
            identifiers[path] = [path] + [identifiers.get("/".join(path.split("/")[:-1]), path)]
        else:
            min_determinant = next(fd[0] for fd in fds if fd[1] == path)
            if any(set([path, *min_determinant]) <= closure for closure in gamma_closures):
                identifiers[path] = min_determinant
            else:
                identifiers[path] = path
    return identifiers

# Define the watermark embedding function
def hash_value(value, key):
    return int(hashlib.sha256(f"{value}{key}".encode()).hexdigest(), 16)

def embed_watermark(data, phi, key, watermark):
    for record in data:
        for field in record:
            if isinstance(record[field], str):
                for i in range(len(record[field])):
                    if random.random() < phi:
                        pos = hash_value(f"{field}-{i}", key) % len(record[field])
                        bit = watermark[hash_value(f"{field}-{i}", key) % len(watermark)]
                        record[field] = record[field][:pos] + str(bit) + record[field][pos + 1:]
    return data

# Define the watermark detection function
def detect_watermark(data, phi, key, watermark_length):
    detected_watermark = [0] * watermark_length
    for record in data:
        for field in record:
            if isinstance(record[field], str):
                for i in range(len(record[field])):
                    if random.random() < phi:
                        pos = hash_value(f"{field}-{i}", key) % len(record[field])
                        bit_position = hash_value(f"{field}-{i}", key) % watermark_length
                        detected_watermark[bit_position] += 1 if record[field][pos] == '1' else -1
    return [1 if bit > 0 else 0 for bit in detected_watermark]

# Example usage
schema = ["title", "author", "journal", "year"]
fds = [("title", "article"), ("author", "article")]
query_templates = [["title", "author"], ["title", "journal"]]
gamma = 0.5

identifiers = create_identifier(schema, fds, query_templates, gamma)
print("Identifiers:", identifiers)

phi = 0.1
key = "secret"
watermark = [1, 0, 1, 1]

watermarked_data = embed_watermark(data, phi, key, watermark)
print(json.dumps(watermarked_data, indent=2))

detected_watermark = detect_watermark(watermarked_data, phi, key, len(watermark))
print("Detected Watermark:", detected_watermark)
