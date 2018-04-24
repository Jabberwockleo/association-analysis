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
import time
import freq_patt_tree as fp
from itertools import chain, combinations
from collections import defaultdict

def update_support_dict(sup_dict, update_dict):
    sup_dict.update(update_dict)

def create_subset_generator(itemset, subset_size=None):
    if subset_size is None:
        return chain(*[combinations(itemset, i + 1) for i in range(len(itemset))])
    else:
        return chain(*[combinations(itemset, subset_size)])

def join_itemsets_with_fixed_elem_size(itemsets, elem_size):
    joint_itemsets = set()
    for a in itemsets:
        for b in itemsets:
            candidate = a.union(b)
            if len(candidate) == elem_size:
                # prune redundant branch
                pruned = False
                if candidate in joint_itemsets:
                    continue
                for elem in create_subset_generator(candidate, subset_size=elem_size - 1):
                    subset = frozenset(elem)
                    if subset not in itemsets:
                        pruned = True
                if not pruned:
                    joint_itemsets.add(candidate)
    return joint_itemsets

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
    update_dict = defaultdict(int) # only needs to record subsets of large_itemsets
    for itemset in candidate_itemsets:
        for actionset in actionsets: # drawback: time consuming
            if itemset.issubset(actionset):
                count_dict[itemset] += 1
    #list_len = len(actionsets)
    for itemset, count in count_dict.items():
        #sup = float(count) / list_len
        sup = count
        if sup >= min_sup:
           itemsets.add(itemset)
           update_dict[itemset] = count
    return itemsets, update_dict

def load_file(fname):
    fd = open(fname, 'r')
    for line in fd:
        line = line.strip().rstrip(',')
        actionset = frozenset(line.split(','))
        yield actionset

def dump(itemset, rules, to_file_only=False):
    fn_items = "out_large_itemsets.csv"
    fn_rules = "out_recom_rules.csv"
    fd_items = open(fn_items, 'w')
    fd_rules = open(fn_rules, 'w')
    for sup, items in sorted(itemset, key=lambda x: x[0]):
        if to_file_only == False:
            print("Itemset: {} support: {:.3f}".format(items, sup))
        fd_items.write(str(sup) + ',')
        fd_items.write(','.join(items))
        fd_items.write('\n')
    fd_items.close()
    for con, rule in sorted(rules, key=lambda x: x[0]):
        items, recom = rule
        if to_file_only == False:
            print("Rule: {} => {} confidence: {:.3f}".format(items, recom, con))
        fd_rules.write(str(con) + ',')
        fd_rules.write('|'.join(items) + ',')
        fd_rules.write('|'.join(recom))
        fd_rules.write('\n')
    fd_rules.close()

def compute_large_itemsets(seed_itemsets, actionsets, min_support):
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
    return support_dict

def run(data_iter, min_support, min_confidence, use_fp_tree=True, output_support_only=False):
    support_dict = {}
    if use_fp_tree == False:
        seed_itemsets, actionsets = generate_seed_itemsets_and_actionsets(data_iter)
        support_dict = compute_large_itemsets(seed_itemsets, actionsets, min_support)
        print('len(support_dict):', len(support_dict))
    else:
        root, header = fp.create_tree(data_iter, min_support)
        support_dict = fp.compute_large_itemsets(root, header, min_support)
        print('len(support_dict):', len(support_dict))

    large_itemsets_with_support = []
    recommendation_rules_with_confidence = []
    
    for itemset, support in support_dict.items():
        large_itemsets_with_support.append((support, tuple(itemset)))
    
    if output_support_only:
        return large_itemsets_with_support, recommendation_rules_with_confidence

    for itemset, support in support_dict.items():
        sup_itemset = support
        for sub in create_subset_generator(itemset):
            subset = frozenset(sub)
            if len(itemset) > len(subset):
                if subset not in support_dict:
                    print('== subset not in:')
                    print('itemset:', itemset)
                    print('-subset', subset)
                    continue
                sup_subset = support_dict[subset]
                confidence = 1.0 * sup_itemset / sup_subset
                if confidence >= min_confidence:
                    recom_candidate = itemset.difference(subset)
                    recommendation_rules_with_confidence.append(
                        (confidence, (tuple(subset), tuple(recom_candidate))))
    return large_itemsets_with_support, recommendation_rules_with_confidence

def run_(data_iter, min_support, min_confidence, use_fp_tree=True, output_support_only=False):
    seed_itemsets, actionsets = generate_seed_itemsets_and_actionsets(data_iter)
    large_itemsets_dict, support_dict = compute_large_itemsets(seed_itemsets, actionsets, min_support)

    large_itemsets_with_support = []
    recommendation_rules_with_confidence = []

    for length, itemsets in large_itemsets_dict.items():
        large_itemsets_with_support.extend(
            [(support_dict[itemset], tuple(itemset)) for itemset in itemsets])
    
    if output_support_only:
        return large_itemsets_with_support, recommendation_rules_with_confidence
            
    for length, itemsets in large_itemsets_dict.items():
        for itemset in itemsets:
            sup_itemset = support_dict[itemset]
            for subset in create_subset_generator(itemset):
                subset = frozenset(subset)
                if len(itemset) > len(subset):
                    sup_subset = support_dict[subset]
                    confidence = 1.0 * sup_itemset / sup_subset
                    if confidence >= min_confidence:
                        recom_candidate = itemset.difference(subset)
                        recommendation_rules_with_confidence.append(
                            (confidence, (tuple(subset), tuple(recom_candidate))))
    return large_itemsets_with_support, recommendation_rules_with_confidence