
U = [
    "Root/inproceedings[title]/author",
    "Root/inproceedings[author]",
    "Root/inproceedings[conference]/title"
     ]


def create_identifier_basic(schema, fds, query_templates):
    identifiers = {}
    for path in schema:
        if not any(path in qt for qt in query_templates):
            identifiers[path] = None
        elif not any(fd[1] == path for fd in fds):
            identifiers[path] = path
        else:
            min_determinant = next(fd[0] for fd in fds if fd[1] == path)
            if any(path in qt and all(det in qt for det in min_determinant) for qt in query_templates):
                identifiers[path] = min_determinant
            else:
                identifiers[path] = path
    return identifiers

def create_identifier_extended(schema, fds, query_templates, gamma):
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


import hashlib


def hash_value(value, key):
    return int(hashlib.sha256(f"{value}{key}".encode()).hexdigest(), 16)


def embed_watermark(xml_data, phi, key, watermark):
    lsb_positions = [(node, pos) for node in xml_data for pos in range(len(node['value']))]
    selected_positions = [pos for pos in lsb_positions if hash_value(pos, key) % 100 < phi * 100]

    for (node, pos) in selected_positions:
        watermark_bit = watermark[hash_value((node, pos), key) % len(watermark)]
        node['value'][pos] = watermark_bit

    return xml_data


def detect_watermark(xml_data, query_set, phi, key, watermark_length):
    detected_watermark = [0] * watermark_length
    lsb_positions = [(node, pos) for node in xml_data for pos in range(len(node['value']))]
    selected_positions = [pos for pos in lsb_positions if hash_value(pos, key) % 100 < phi * 100]

    for (node, pos) in selected_positions:
        bit_position = hash_value((node, pos), key) % watermark_length
        detected_watermark[bit_position] += 1 if node['value'][pos] == 1 else -1

    return [1 if bit > 0 else 0 for bit in detected_watermark]


# Example usage
schema = ["db/book/title", "db/book/author", "db/book/publisher"]
fds = [("db/book/title", "db/book"), ("db/book/editor", "db/book/publisher")]
query_templates = [["db/book/title", "db/book/author"], ["db/book/title", "db/book/publisher"]]
gamma = 0.5
xml_data = [{"value": [0, 1, 0, 1]}, {"value": [1, 0, 1, 0]}]  # Simplified XML data
phi = 0.1
key = "secret"
watermark = [1, 0, 1, 1]

identifiers = create_identifier_extended(schema, fds, query_templates, gamma)
watermarked_data = embed_watermark(xml_data, phi, key, watermark)
detected_watermark = detect_watermark(watermarked_data, query_templates, phi, key, len(watermark))

print("Original XML Data:", xml_data)
print("Watermarked XML Data:", watermarked_data)
print("Detected Watermark:", detected_watermark)
