#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2018 Wan Li. All Rights Reserved
#
########################################################################

"""
File: apriori.py
Author: Wan Li
Date: 2018/04/11 08:24:31
"""

import sys
from itertools import chain, combinations
from collections import defaultdict

def update_support_dict(sup_dict, update_dict):
    sup_dict.update(update_dict)
    
def join_itemsets_with_fixed_elem_size(itemsets, elem_size):
    joint_itemsets = set()
    for a in itemsets:
       for b in itemsets:
           candidate = a.union(b)
           if len(candidate) == elem_size:
               joint_itemsets.add(candidate)
    return joint_itemsets

def create_subset_generator(itemset):
    return chain(*[combinations(itemset, i + 1) for i in range(len(itemset))])

def generate_seed_itemsets_and_actionsets(data_iter):
    actionsets = list() # type list
    seed_itemsets = set() # type set
    for actionlist in data_iter:
        actionset = frozenset(actionlist)
        actionsets.append(actionset)
        for item in actionset:
            seed_itemsets.add(frozenset([item]))
    return seed_itemsets, actionsets

def get_support_itemsets(candidate_itemsets, actionsets, min_sup):
    itemsets = set()
    count_dict = defaultdict(int)
    for itemset in candidate_itemsets:
        for actionset in actionsets:
            if itemset.issubset(actionset):
                count_dict[itemset] += 1
    list_len = len(actionsets)
    for itemset, count in count_dict.items():
        sup = float(count) / list_len
        if sup >= min_sup:
           itemsets.add(itemset)
    return itemsets, count_dict

def load_file(fname):
    fd = open(fname, 'r')
    for line in fd:
        line = line.strip().rstrip(',')
        actionlist = frozenset(line.split(','))
        yield actionlist

def dump(itemset, rules):
    for sup, items in sorted(itemset, key=lambda x: x[0]):
        print("Itemset: {} support: {:.3f}".format(items, sup))
    for con, rule in sorted(rules, key=lambda x: x[0]):
        items, recom = rule
        print("Rule: {} => {} support: {:.3f}".format(items, recom, con))

def run(data_iter, min_support, min_confidence):
    seed_itemsets, actionsets = generate_seed_itemsets_and_actionsets(data_iter)
    actionsets_size = len(actionsets)
    support_dict = defaultdict(int)
    large_itemsets_dict = dict() # key: length val: set of itemset
    # seeding
    seed_sup_itemsets, update_dict = get_support_itemsets(
        seed_itemsets, actionsets, min_support)
    update_support_dict(support_dict, update_dict)
    # compute larget itemsets
    cur_large_itemsets = seed_sup_itemsets
    cur_itemsets_size = 1
    # all size-1 subset of large_itemsets must be large_itemsets
    while (len(cur_large_itemsets) != 0):
        large_itemsets_dict[cur_itemsets_size] = cur_large_itemsets
        cur_itemsets_size += 1
        candidate_itemsets = join_itemsets_with_fixed_elem_size(
            cur_large_itemsets, cur_itemsets_size)
        cur_large_itemsets, update_dict = get_support_itemsets(
            candidate_itemsets, actionsets, min_support)
        update_support_dict(support_dict, update_dict)

    large_itemsets_with_support = []
    recommendation_rules_with_confidence = []
    for length, itemsets in large_itemsets_dict.items():
        large_itemsets_with_support.extend(
            [(1.0 * support_dict[itemset] / actionsets_size, tuple(itemset)) for itemset in itemsets])
        for itemset in itemsets:
            sup_itemset = 1.0 * support_dict[itemset] / actionsets_size
            for subset in create_subset_generator(itemset):
                subset = frozenset(subset)
                recom_candidate = itemset.difference(subset)
                if len(recom_candidate) > 0:
                    sup_subset = 1.0 * support_dict[subset] / actionsets_size
                    confidence = sup_itemset / sup_subset
                    if confidence >= min_confidence:
                        recommendation_rules_with_confidence.append(
                            (confidence, (tuple(subset), tuple(recom_candidate))))

    return large_itemsets_with_support, recommendation_rules_with_confidence