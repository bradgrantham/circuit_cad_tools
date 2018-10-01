import csv
import sys

# Brad's fields: Reference, Value, Footprint, Datasheet, Manufacturer, Manufacturer PN, Distributor, Distributor PN, Distributor URL, Description, Package, Type

bom = {}

csvreader = csv.reader(sys.stdin)

headers = csvreader.next()[1:]
headers.insert(0, 'Item')
headers.insert(1, 'Ref Des')
headers.insert(2, 'Qty')

for row in csvreader:
    reference = row[0]
    otherfields = row[1:-1]
    key = " ".join(otherfields)
    bomentry = bom.setdefault(key, [[], otherfields])
    bomentry[0].append(reference)

print headers
print ", ".join(headers)
item = 0
for (key, (refs, fields)) in bom.iteritems():
    print '%d, ' % item,
    print '"%s", ' % (", ".join(refs)), 
    print '%d, ' % len(refs),
    print ", ".join(fields)
    item = item + 1
