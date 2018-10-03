import csv
import sys

# Input fields (for validation)
input_field_names = ["Reference", "Value", "Footprint", "Do Not Place", "Datasheet", "Manufacturer", "Manufacturer PN", "Distributor", "Distributor PN", "Distributor URL", "Description", "Package", "Type"]

# Output fields
output_field_names = ["Item", "Ref Des", "Qty", "Value", "Footprint", "Do Not Place", "Datasheet", "Manufacturer", "Manufacturer PN", "Distributor", "Distributor PN", "Distributor URL", "Description", "Package", "Type"]

bom = {}

csvreader = csv.DictReader(sys.stdin)

for part in csvreader:
    for (field_name, field_value) in part.iteritems():
        if field_name[0] == ' ':
            del part[field_name]
            field_name = field_name[1:]
            part[field_name] = field_value
        if field_name not in input_field_names:
            print "field '%s' in input file is not in input field_names" % field_name
            sys.exit(1)
    reference = part['Reference']
    unique = part
    del unique['Reference']
    for field in unique.iterkeys():
        if not unique[field]:
            unique[field] = ""
    key_parts = [unique.get(field, "") for field in sorted(unique.iterkeys())]
    key = " ".join(key_parts)
    entry = bom.setdefault(key, {"refs" : [], "partfields" : unique})
    entry["refs"].append(reference)

writer = csv.DictWriter(sys.stdout, output_field_names)

writer.writeheader()
item = 0
for (key, entry) in bom.iteritems():
    bom_entry = entry["partfields"]
    refs = entry["refs"]
    bom_entry["Item"] = item
    bom_entry["Ref Des"] = ",".join(refs)
    bom_entry["Qty"] = len(refs)
    writer.writerow(bom_entry)
    item = item + 1
