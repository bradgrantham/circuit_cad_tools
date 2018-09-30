import csv
import sys

bom = {}

reader = csv.reader(sys.stdin)
header = next(reader)

columns = {}
for (column_name, column_number) in zip(header, range(0, len(header))):
    columns[column_name.strip()] = column_number

# Digikey ignores the headers and makes one map columns, so this
# is unnecessary and also annoying.
# print ",".join(("Digi-Key Part Number", "Manufacturer Name", "Manufacturer Part Number", "Customer Reference", "Quantity 1", "Quantity 2", "Quantity 3"))

for row in reader:
    entry = {}
    for (column_name, column_number) in columns.iteritems():
        if column_number < len(row):
            entry[column_name] = row[column_number].strip()
        else:
            entry[column_name] = ""
    dist = entry.get('Distributor', '')
    distpn = entry.get('Distributor PN', '')
    mfg = entry.get('Manufacturer', '')
    pn = entry.get('PN', '')
    value = entry.get('Value', '')
    if dist != 'Digikey':
        print >>sys.stderr, "no digikey part number for reference %s, value %s footprint %s"% (entry['Reference'], entry['Value'], entry['Footprint'])
    else:
        bom.setdefault(dist + distpn + mfg + pn, []).append(entry)

for (ref, entries) in bom.iteritems():
    dist = entries[0].get('Distributor', '')
    distpn = entries[0].get('Distributor PN', '')
    mfg = entries[0].get('Manufacturer', '')
    pn = entries[0].get('PN', '')
    refs = " ".join([ref['Reference'] for ref in entries])
    print ",".join((distpn, mfg, pn, refs, str(len(entries)), "10", "100"))
