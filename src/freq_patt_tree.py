#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2018 Wan Li, Inc. All Rights Reserved
#
########################################################################

"""
File: freq_patt_tree.py
Author: Wan Li
Date: 2018/04/12 16:15:48
"""

from collections import defaultdict

ROOT_NODE_NAME = "ROOT"

class Node:
    def __init__(self, name, count, parent):
        self.name = name
        self.count = count
        self.next = None # header chain
        self.parent = parent
        self.children = {}

    def increment(self, count):
        self.count += count

    def dump(self, indent=1, func=None, fd=None):
        """
            Print tree
            Params:
                func: optional function (name) -> string
                fd: file descriptor
        """
        if fd is None:
            fd = open('out_fptree.txt', 'w')
        content = '-'*indent + self.name + ':' + str(self.count)
        print(content)
        if func is not None:
            content += ' info:' + func(self.name)
        fd.write(content)
        fd.write('\n')
        for ch in self.children.values():
            ch.dump(indent=indent+1, func=func, fd=fd)
        if indent == 1:
            fd.close()

def load_file(fname):
    fd = open(fname, 'r')
    for line in fd:
        line = line.strip().rstrip(',')
        actionset = frozenset(line.split(','))
        yield actionset

def update_header(cur_node, new_node):
    while (cur_node.next is not None):
        cur_node = cur_node.next
    cur_node.next = new_node

def update_tree(current_node, header, ordered_actions, actionset_count, largeitem_count_dict):
    if len(ordered_actions) == 0:
        pass
    item = ordered_actions[0][0]
    # update children
    if item in current_node.children:
        current_node.children[item].increment(actionset_count)
    else:
        current_node.children[item] = Node(item, actionset_count, current_node)
        # update header
        if item not in header:
            header[item] = current_node.children[item]
        else:
            update_header(header[item], current_node.children[item])
    if len(ordered_actions) > 1:
        update_tree(current_node.children[item], header,
            ordered_actions[1::], actionset_count, largeitem_count_dict)

def build_fp_tree(actionset_count_dict, min_sup=2):
    header = {} # key: name val: node
    item_count_dict = defaultdict(int)
    largeitem_count_dict = defaultdict(int)
    largeitemset = set()
    # count
    for actionset, actionset_count in actionset_count_dict.items():
        for item in actionset:
            item_count_dict[item] += actionset_count
    # prune
    for k, v in item_count_dict.items():
        if v >= min_sup:
            largeitem_count_dict[k] = v
            largeitemset.add(k)
    if len(largeitemset) == 0:
        return None, None
    # init tree
    root = Node(ROOT_NODE_NAME, 1, None)
    # build tree
    for actionset, actionset_count in actionset_count_dict.items():
        # sort current actionset
        actions = []
        for action in actionset:
            if action in largeitem_count_dict:
                actions.append(action)
        if len(actions) == 0:
            continue
        ordered_actions = sorted([(action, largeitem_count_dict[action]) for action in actions],
            key=lambda x: x[1], reverse=True)
        update_tree(root, header, ordered_actions, actionset_count, largeitem_count_dict)
    return root, header
    
def create_tree(data_iter, min_sup=2):
    actionset_count_dict = defaultdict(int)
    # count
    for actionset in data_iter:
        actionset_count_dict[actionset] += 1
    return build_fp_tree(actionset_count_dict, min_sup)

def ascend(node, prefixes):
      if node.parent is not None:
          prefixes.append(node.name)
          ascend(node.parent, prefixes)

def conditional_pattern_base(header_node):
    conditional_paths = {}
    header_node_count = 0
    node = header_node
    while node is not None:
        prefixes = []
        ascend(node, prefixes)
        if len(prefixes) > 1:
            conditional_paths[frozenset(prefixes[1:])] = node.count
        header_node_count += node.count
        node = node.next
    return conditional_paths, header_node_count

def compute_large_itemsets(root, header, min_sup=2):
    if root is None:
        return {}
    large_itemset_dict = defaultdict(int) # key: itemset val: support
    for name, node in header.items():
        conditional_paths, header_node_count = conditional_pattern_base(node)
        sub_root, sub_header = build_fp_tree(conditional_paths, min_sup)
        items_dict = compute_large_itemsets(sub_root, sub_header, min_sup)
        update_dict = defaultdict(int)
        
        # create single set with current count
        update_dict[frozenset([node.name])] += header_node_count

        # append current node.name to every key, retain count
        for k, v in items_dict.items():
            new_k = set(k)
            new_k.add(node.name)
            update_dict[frozenset(new_k)] += v
        
        # update final dict
        for k, v in update_dict.items():
            large_itemset_dict[k] += v
    return large_itemset_dict