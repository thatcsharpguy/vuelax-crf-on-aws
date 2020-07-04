from collections import defaultdict

import csv

offer_id_tokens = defaultdict(list)
with open("data/to_label-done.csv") as fd:
    reader = csv.reader(fd)
    next(reader)
    for entry in reader:
        offer_id_tokens[int(entry[0])].append(entry[4])

offers = []
with open("data/vuelos.csv") as fd:
    reader = csv.reader(fd)
    next(reader)
    for entry in reader:
        offers.append(entry[1])

features = text.transform(offers[:10])

for idx, feats in enumerate(features):
    if idx not in offer_id_tokens:
        break
    if len(feats) != len(offer_id_tokens[idx]):
        import pdb

        pdb.set_trace()
        pass
    assert len(feats) == len(offer_id_tokens[idx])
