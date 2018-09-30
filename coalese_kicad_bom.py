import csv
import sys

bom = {}
for row in csv.reader(sys.stdin):
# Reference, Value, Footprint, Datasheet, Part
    bom.setdefault(" ".join([row[1], row[2]]), []).append(row)

for (part, refs) in bom.iteritems():
    print part
