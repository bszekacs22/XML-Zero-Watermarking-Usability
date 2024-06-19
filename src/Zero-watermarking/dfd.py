import lxml.etree as ET
import utils
from collections import deque
import shelve


def candidateLHS(A, FDs):
    Ls = set()  # Initialize an empty set to hold the LHS candidates
    for a in A:
        AL = A - {a}
        Ls.add(AL)
        if not FDs:
            Ls.add(frozenset(AL))
        for fd in FDs:
            L, r = fd[0], fd[1]
            if a == r and AL.issubset(L):
                continue
            elif A.issubset(L):
                continue
            else:
                Ls.add(frozenset(AL))  # Use frozenset to ensure AL is hashable
    return Ls


def maxgroupsize(d):
    res = 1
    for att in d.keys():
        res = max(res, len(d[att]))
    return res

def deletegroupsofone(d):
    for att in list(d.keys()):
        if len(d[att]) == 1:
            del d[att]
    return d

def discover_fd(Rp, tag):
    # Step 1: Generate attribute partitions
    attribute_partitions = utils.generate_attribute_partitions(Rp, tag)
    # Delete partitions w 1 element
    for att in attribute_partitions.keys():
        attribute_partitions[att] = deletegroupsofone(attribute_partitions[att])


    # Step 2: Initialize sets and queue
    Keys = set()
    FDs = set()
    Q = deque()
    attributes = sorted(list(attribute_partitions.keys()), key=max)

    # Step 3: Enqueue single attribute nodes
    for attr in attributes:
        if maxgroupsize(attribute_partitions[attr]) == 1:
            Keys.add(attr)
            continue
        Q.append(attr)

    # Step 4: Process the queue
    while Q:
        A = Q.popleft()
        if A not in attribute_partitions:
            # ΠA needs to be generated
            Ls = candidateLHS(A, FDs)
            if not Ls:
                continue  # No need to expand A

            A1 = sorted(list(Ls), key=max)[0]
            attribute_partitions = utils.combine_attribute_partitions(A-A1, A1, attribute_partitions)

            #attribute_partitions[A] = deletegroupsofone(attribute_partitions[A])

        if maxgroupsize(attribute_partitions[A]) == 1:
            Keys.add(A)
            continue
        deletegroupsofone(attribute_partitions[A])

        Ls = candidateLHS(A, FDs)

        for AL in Ls:
            r = A - AL
            left = list(attribute_partitions[AL].values())
            right = list(attribute_partitions[A].values())
            if left == right:
                FDs.add((AL,r))

        ak = max(A)
        k = attributes.index(frozenset({ak}))
        for i in range(k+1, len(attributes)):
            A_prime = A | attributes[i]
            if not any(K.issubset(A_prime) for K in Keys):
                Q.append(A_prime)

    print(len(FDs))
    return Keys, FDs

def collect_unique_tags(node, unique_tags):
    # Add the tag of the current node to the set
    unique_tags.add(node.tag)
    # Recursively process each child node
    for child in node:
        collect_unique_tags(child, unique_tags)

def get_unique_tags(root):
    unique_tags = set()
    collect_unique_tags(root, unique_tags)
    unique_tags
    return unique_tags

# discover all intra-relation functional dependencies
def discoverFD(tag):
    parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
    tree = ET.parse('../../data/dblp_smal.xml', parser)
    root = tree.getroot()
    inproceedings_count = count_specific_elements(root, 'inproceedings')
    print(f"Number of 'inproceedings' elements in the XML: {inproceedings_count}")
    keys, fds = discover_fd(root, tag)
    return keys, fds


def count_specific_elements(node, tag):
    count = 1 if node.tag == tag else 0  # Count the current node if it matches the tag
    for child in node:
        count += count_specific_elements(child, tag)
    return count


# keys, fds = discoverFD('inproceedings')
# print("Keys:", keys)
# print("FDs:", fds)
# print(len(keys))
# print(len(fds))




