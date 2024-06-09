import lxml.etree as ET
import utils
from collections import deque


def candidateLHS(A, FDs):
    Ls = set()  # Initialize an empty set to hold the LHS candidates
    for a in A:
        AL = A - {a}
        for fd in FDs:
            L, r = fd['LHS'], fd['RHS']
            if a == r and AL.issubset(L):
                continue
            elif A.issubset(L):
                continue
            else:
                Ls.add(frozenset(AL))  # Use frozenset to ensure AL is hashable
    return Ls


def discover_fd(Rp):
    # Step 1: Generate attribute partitions
    attribute_partitions = utils.generate_attribute_partitions(Rp, "inproceedings")

    # Step 2: Initialize sets and queue
    Keys = set()
    FDs = set()
    Q = deque()
    attributes = list(attribute_partitions.keys())

    # Step 3: Enqueue single attribute nodes
    for attr in attributes:
        Q.append(attr)

    # Step 4: Process the queue
    while Q:
        A = Q.popleft()

        if A not in attribute_partitions:
            # ΠA needs to be generated
            Ls = candidateLHS(A, FDs)
            if not Ls:
                continue  # No need to expand A

            if len(Ls) == 1:
                A1 = next(iter(Ls))
                attribute_partitions[A] = attribute_partitions[A - A1] & attribute_partitions[A1]
            else:
                A1, A2 = list(Ls)[:2]
                attribute_partitions[A] = attribute_partitions[A1] & attribute_partitions[A2]

        if len(attribute_partitions[A]) == 1:
            Keys.add(A)
            continue

        Ls = candidateLHS(A, FDs)

        for AL in Ls:
            r = A - AL
            if attribute_partitions[AL] == attribute_partitions[A]:
                FDs.add({'LHS': AL, 'RHS': r})

        ak = max(A)
        k = attributes.index(frozenset({ak}))
        for i in range(k+1, len(attributes)):
            A_prime = A | attributes[i]
            if not any(K.issubset(A_prime) for K in Keys):
                Q.append(A_prime)

    return Keys, FDs



parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
tree = ET.parse('../../data/test.xml', parser)
root = tree.getroot()


keys, fds = discover_fd(root)
print("Keys:", keys)
print("FDs:", fds)
