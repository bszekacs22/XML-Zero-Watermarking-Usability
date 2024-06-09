from collections import defaultdict

import lxml.etree as ET


class PartitionTarget:
    def __init__(self, fd, fd_target=None, key_target=None):
        self.fd = fd  # Functional Dependency: LHS -> RHS
        self.fd_target = fd_target if fd_target else set()  # Inequalities needed for inter-relation FD
        self.key_target = key_target if key_target else set()  # Additional inequalities for inter-relation Key

    def add_fd_target(self, target):
        self.fd_target.add(target)

    def add_key_target(self, target):
        self.key_target.add(target)


def add_key_ineqs(IDp, pt, g):
    if len(g) == 1 or pt.key_target == 'invalid':
        return

    for t1 in g:
        for t2 in g:
            if t1 != t2:
                t1_prime = IDp.get(t1)
                t2_prime = IDp.get(t2)
                if t1_prime == t2_prime:
                    pt.key_target = 'invalid'
                    return
                else:
                    pt.add_key_target(f"{t1_prime}!={t2_prime}")


def createPT(IDp, AL, A, Cp):
    pt = PartitionTarget()
    pt.fd = {"LHS": AL, "RHS": A - AL}

    for g1 in Cp:
        for g2 in [g for g in Cp if g.issubset(g1)]:
            add_key_ineqs(IDp, pt, g2)
            if g1 != g2:
                g1 = g1 - g2
                for t1 in g1:
                    for t2 in g2:
                        t1_prime = IDp.get(t1)
                        t2_prime = IDp.get(t2)
                        if t1_prime == t2_prime:
                            return None
                        else:
                            pt.add_fd_target(f"{t1_prime}!={t2_prime}")
                if g1:
                    add_key_ineqs(IDp, pt, g1)
    return pt


def updatePT(IDp, pt, PA):
    pt_prime = PartitionTarget(fd=pt.fd)

    for inequality in pt.fd_target:
        t1, t2 = inequality.split('!=')
        if not PA.satisfies(t1, t2):  # Assuming ΠA has a satisfies method
            t1_prime = IDp.get(t1)
            t2_prime = IDp.get(t2)
            if t1_prime == t2_prime:
                return None
            else:
                pt_prime.add_fd_target(f"{t1}!={t2}")

    for inequality in pt.key_target:
        t1, t2 = inequality.split('!=')
        if not PA.satisfies(t1, t2):  # Assuming ΠA has a satisfies method
            t1_prime = IDp.get(t1)
            t2_prime = IDp.get(t2)
            if t1_prime == t2_prime:
                pt_prime.key_target = 'invalid'
                break
            else:
                pt_prime.add_key_target(f"{t1}!={t2}")

    return pt_prime


def extract_letters(lhs, rhs):
    # Extracts only the letters from the LHS and RHS strings
    return ''.join(filter(str.isalpha, lhs + rhs))


def collect_data_elements(tree):
    elements_data = []
    for elem in tree.iter():
        path = tree.getpath(elem)
        value = elem.text if elem.text else ""
        elements_data.append((path, value))
    return elements_data

def partition_by_lhs(data_elements):
    lhs_partitions = defaultdict(PartitionTarget)
    for path, value in data_elements:
        lhs_value = extract_letters(path, value)
        if lhs_value not in lhs_partitions:
            lhs_partitions[lhs_value] = PartitionTarget(fd={"LHS": path, "RHS": ""})
        lhs_partitions[lhs_value].add_fd_target((path, value))
    return lhs_partitions

def discover_xfd(tree):
    data_elements = collect_data_elements(tree)
    lhs_partitions = partition_by_lhs(data_elements)
    attribute_partitions = generate_attribute_partitions(tree)

    fds = []

    for AL in lhs_partitions:
        for A in data_elements:
            if AL != A:
                Cp = attribute_partitions[A]
                pt = createPT(lhs_partitions, AL, A, Cp)
                if pt:
                    pt_prime = updatePT(lhs_partitions, pt, attribute_partitions[AL])
                    if pt_prime:
                        fds.append(pt_prime)

    return fds


def collect_attribute_data(root):
    attributes_data = []

    def traverse(node, current_path):
        for attr_name, attr_value in node.attrib.items():
            path = f"{current_path}/@{attr_name}"
            attributes_data.append((path, attr_value))

        for child in node:
            traverse(child, f"{current_path}/{child.tag}")

    traverse(root, root.tag)
    return attributes_data


def partition_attributes(attributes_data):
    attribute_partitions = defaultdict(set)

    for path, value in attributes_data:
        attribute_partitions[path].add(value)

    return attribute_partitions


def generate_attribute_partitions(root):
    attributes_data = collect_attribute_data(root)
    attribute_partitions = partition_attributes(attributes_data)

    return attribute_partitions

# Example usage
parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
tree = ET.parse('../../data/test.xml', parser)
root = tree.getroot()


attribute_partitions = generate_attribute_partitions(root)
for path, values in attribute_partitions.items():
    print(f"Path: {path}, Values: {values}")

fds = discover_xfd(tree)
for fd in fds:
    print(fd)