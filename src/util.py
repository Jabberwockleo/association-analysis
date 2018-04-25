#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2018 Wan Li, Inc. All Rights Reserved
#
########################################################################

"""
File: util.py
Author: Wan Li
Date: 2018/04/13 21:47:40
"""

import numpy as np
from scipy import sparse

def create_itemset_from_file(fn):
    itemset = set()
    fd = open(fn, 'r')
    for line in fd:
        for e in line.rstrip().split(','):
            itemset.add(e)
    fd.close()
    return itemset

def create_itemset_from_iterator(data_iter):
    itemset = set()
    for actionset in data_iter:
        for e in actionset:
            itemset.add(e)
    return itemset

def yield_itemsets_from_file(fn):
    fd = open(fn, 'r')
    for line in fd:
        yield set(line.rstrip().split(','))
    fd.close()

def create_itemset_from_dataframe(df):
    itemset = set()
    for index, row in df.iterrows():
        for e in row.tolist():
            itemset.add(e)
    itemset.remove(np.nan)
    return itemset

def create_onehot_vector(itemset):
    items = list(itemset)
    itemmat = sparse.eye(len(items))
    itemvec_dict = {}
    for i in range(len(items)):
        itemvec_dict[items[i]] = itemmat.getrow(i)
    return itemvec_dict

def yield_actionsets_from_file(fn):
    fd = open(fn, "r")
    for line in fd:
        yield frozenset(line.rstrip().split(',')[1].split('|'))
    fd.close()

def create_user_item_matrix(user_action_sets, uservec_dict, itemvec_dict, mimic="SVD++"):
    """
        Create factorization machine's data format

        Params:
            user_action_sets: array of tuple (uid, actionset)
    """
    mat = None
    for uid, items in user_action_sets:
        vu = uservec_dict[index]
        vi_sum = None
        if mimic != "MF":
            for item_name in items:
                if item_name is np.nan:
                    continue
                vi = itemvec_dict[item_name]
                if vi_sum is None:
                    vi_sum = vi
                else:
                    vi_sum += vi
        if mimic == "SVD++":
            vi_sum /= np.sqrt(np.sum(vi_sum))
        for item_name in items:
            if item_name is np.nan:
                continue
            vi = itemvec_dict[item_name]
            if mimic == "SVD++":
                vuil = sparse.hstack((vu, vi, vi_sum))
            elif mimic == "MF":
                vuil = sparse.hstack((vu, vi))
            if mat is None:
                mat = vuil
            else:
                mat = sparse.vstack((mat, vuil))
    return mat

def create_user_item_matrix_with_compact_sid(df, uservec_dict, itemvec_dict, mimic="SVD++"):
    mat = None
    for index, row in df.iterrows():
        vu = uservec_dict[index]
        vi_sum = None
        if mimic != "MF":
            for item_name in row['sid'].split(','):
                if item_name is np.nan:
                    continue
                vi = itemvec_dict[item_name]
                if vi_sum is None:
                    vi_sum = vi
                else:
                    vi_sum += vi
        if mimic == "SVD++":
            vi_sum /= np.sqrt(np.sum(vi_sum))
        for item_name in row['sid'].split(','):
            if item_name is np.nan:
                continue
            vi = itemvec_dict[item_name]
            if mimic == "SVD++":
                vuil = sparse.hstack((vu, vi, vi_sum))
            elif mimic == "MF":
                vuil = sparse.hstack((vu, vi))
            if mat is None:
                mat = vuil
            else:
                mat = sparse.vstack((mat, vuil))
    return mat

def create_user_item_predict_matrix_with_compact_sid(uid, df_sid, uservec_dict, itemvec_dict, mimic="SVD++"):
    mat = None
    vu = uservec_dict[uid]
    if True:
        vi_sum = None
        if mimic != "MF":
            for item_name in df_sid.loc[uid]['sid'].split(','):
                if item_name is np.nan:
                    continue
                vi = itemvec_dict[item_name]
                if vi_sum is None:
                    vi_sum = vi
                else:
                    vi_sum += vi
        if mimic == "SVD++":
            vi_sum /= np.sqrt(np.sum(vi_sum))
        for item_name in itemvec_dict.keys():
            if item_name is np.nan:
                continue
            vi = itemvec_dict[item_name]
            if mimic == "SVD++":
                vuil = sparse.hstack((vu, vi, vi_sum))
            elif mimic == "MF":
                vuil = sparse.hstack((vu, vi))
            if mat is None:
                mat = vuil
            else:
                mat = sparse.vstack((mat, vuil))
    return mat