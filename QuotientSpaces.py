def eqClass(qspace, eqrel, val):
    for q in qspace:
        if len(q) > 0 and eqrel(val,q[0]) is True:
            return q
    return []