from collections import defaultdict
import shelve
import sqlite3
from lxml import etree as ET
import time
import pandas as pd
import os

def generate_attribute_partitions(root, tag):
    attribute_partitions = defaultdict(dict)

    # Find all nodes with the specified tag (e.g., 'inproceedings')
    nodes = root.findall(f'.//{tag}')

    for node in nodes:
        # Collect the child elements and their text values for each node
        for child in node:
            attr = frozenset({child.tag})
            if child.text:
                value = child.text
                if attr in attribute_partitions.keys():
                    if value in attribute_partitions[attr].keys():
                        attribute_partitions[attr][value] = attribute_partitions[attr][value] | {node}
                    else:
                        attribute_partitions[attr][value] = {node}
                else:
                    attribute_partitions[attr] = {value: {node}}


    return attribute_partitions

def combine_attribute_partitions(key1, key2, parts):
    combinedkey = key1 | key2
    for k1 in parts[key1]:
        for k2 in parts[key2]:
            e1 = parts[key1][k1]
            e2 = parts[key2][k2]
            elems = e1 & e2
            if len(elems) > 1:
                parts[combinedkey][frozenset({k1}) | frozenset({k2})] = elems
    return parts

def generate_attribute_partitions_tags(root, tag, tags):
    attribute_partitions = defaultdict(dict)

    # Find all nodes with the specified tag (e.g., 'inproceedings')
    nodes = root.findall(f'.//{tag}')

    for node in nodes:
        # Collect the child elements and their text values for each node
        for child in node:
            if child.tag in tags:
                attr = frozenset({child.tag})
                if child.text:
                    value = child.text
                    if attr in attribute_partitions.keys():
                        if value in attribute_partitions[attr].keys():
                            attribute_partitions[attr][value] = attribute_partitions[attr][value] | {node}
                        else:
                            attribute_partitions[attr][value] = {node}
                    else:
                        attribute_partitions[attr] = {value: {node}}
    return attribute_partitions