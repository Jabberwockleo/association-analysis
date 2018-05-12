#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#
########################################################################

"""
File: recomm.py
Author: wanli03(wanli03@baidu.com)
Date: 2018/05/10 18:36:03
"""

from collections import defaultdict

def yield_recom_rules(fn):
    """
        Rule iterator generator
    """
    fd = open(fn, "r")
    for line in fd:
        elems = line.strip().split(',')
        confidence = elems[0]
        base = frozenset(elems[1].split('|'))
        recom = frozenset(elems[2].split('|'))
        yield confidence, base, recom


def yield_uid_sids(fn):
    """
        Uid sids iterator generator
    """
    fd = open(fn, "r")
    for line in fd:
        elems = line.strip().split(',')
        uid = elems[0]
        sids = frozenset(elems[1].split('|'))
        yield uid, sids


def build_recom_rules(recom_iter):
    """
        Recomm rule generator
    """
    recom = []
    for c, b, r in recom_iter:
        recom.append(tuple([c, b, r]))
    return recom


def associate_recom(sids, recom_rules):
    """
        Make recomm for single user
    """
    recoms = defaultdict(int) # sid -> confidence
    reason = defaultdict(str)
    for c, b, r in recom_rules:
        if b.issubset(sids):
            for sid in b:
                if recoms[sid] < float(c):
                    recoms[sid] = round(float(c), 2)
                    reason[sid] = b
    return recoms, reason


def recommend(fn_uid_sids, fn_recom_rules):
    """
        Produce recommendation
    """
    recomms = []
    fd = open('out_user_recom.txt', 'w')
    recom_rules = build_recom_rules(yield_recom_rules(fn_recom_rules))
    for uid, sids in yield_uid_sids(fn_uid_sids):
        recoms, reason = associate_recom(sids, recom_rules)
        recom_str = "|".join([":".join([k, str(v), "&".join(reason[k])]) \
                              for k, v in recoms.items()])
        fd.write("{},{}".format(uid, recom_str))
        fd.write("\n")
        recomms.append(tuple([uid, recoms, reason]))
    fd.close()
    return recomms


if __name__ == "__main__":
    recommend('uid_sids.txt', 'out_recom_rules.csv')
