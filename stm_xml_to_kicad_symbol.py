import csv
import re
import sys
import xmltodict

lib_body = """EESchema-LIBRARY Version 2.3
#encoding utf-8
#
# %(description)s
#
DEF %(partname)s U 0 40 Y Y 1 F N
F0 "U" 0 0 60 H V C CNN
F1 "%(partname)s" %(labelX)d %(labelY)d 60 H V L CNN
F2 "" 0 0 60 H V C CNN
F3 "" 0 0 60 H V C CNN
$FPLIST
%(fplist)s$ENDFPLIST
DRAW
S %(left)d %(top)d %(right)d %(bottom)d 0 1 10 f
%(pins)s
ENDDRAW
ENDDEF
#
#End Library"""

# <Mcu ClockTree="STM32H7" DBVersion="V3.0" Family="STM32H7" HasPowerPad="false" IOType="" Line="STM32H743/753" Package="LQFP176" RefName="STM32H743IGTx" xmlns="http://mcd.rou.st.com/modules.php?name=mcu">

package_to_footprint = {
    "LQFP176" : "LQFP*",
}

dcm_body = """EESchema-DOCLIB  Version 2.0
#
#End Doc Library"""

name_fixing_table = str.maketrans(" -/", "___", "()+")

def fixed_name(name):
    return name.translate(name_fixing_table)


pins = {}
pin_positions = []

partname = sys.argv[2]
description = sys.argv[3]

vars = {
    "partname" : partname,
    "description" : description,
}

with open(sys.argv[1]) as fd:
    doc = xmltodict.parse(fd.read())

package = doc['Mcu']['@Package']
if package in package_to_footprint:
    vars["fplist"] = package_to_footprint[package] + "\n"
else:
    vars["fplist"] = ""

power = []
ground = []
other = []
gpios = {}
gpio_pins = []

for p in doc['Mcu']['Pin']:
    position = p['@Position']
    name = p['@Name']
    pin_positions.append(position)
    pins[position] = p
    gpio_match = re.match('P(?P<port>[A-Z])(?P<number>[0-9]+)', name)
    if gpio_match:
        # print(gpio_match.group("port"), gpio_match.group("number"))
        p['PinNumber'] = int(gpio_match.group("number"));
        gpios.setdefault(gpio_match.group("port"), []).append(p)
        gpio_pins.append(p)
    elif re.match('VDD.*', name):
        power.append(p)
    elif re.match('VSS.*', name):
        ground.append(p)
    else:
        other.append(p)

gpio_ports = sorted(gpios.keys())
for (port, pins) in gpios.items():
    pins.sort(key=lambda pin: int(pin['PinNumber']))

labels_sides_margin = 150
gpio_port_layout_margin = 100
pin_label_layout_height = 100
character_layout_length = 44 # measured by hand in footprint editor
left_side_layout_margin = 200
pin_layout_length = 200

def string_layout_length(s) :
    return len(s) * character_layout_length

layout_height_of_other_pin_list = len(other) * pin_label_layout_height
layout_height_of_power_pin_list = len(power) * pin_label_layout_height
layout_height_of_ground_pin_list = len(ground) * pin_label_layout_height

ports_on_right_side = (len(gpios) + 1) // 2
ports_on_left_side = len(gpios) - ports_on_right_side

right_side_gpios_from_bottom = gpio_ports[0:ports_on_right_side]
left_side_gpios_from_bottom = gpio_ports[-ports_on_left_side:]

# print(gpio_ports)
# print(right_side_gpios_from_bottom)
# print(left_side_gpios_from_bottom)

right_side_gpios_from_bottom.reverse()

max_left_right_label_length = 0
for pin in (other + gpio_pins):
    max_left_right_label_length = max(max_left_right_label_length, len(fixed_name(pin['@Name'])))
print("max is %d, %d" % (max_left_right_label_length, max_left_right_label_length * character_layout_length))

def number_of_gpio_pins(list):
    count = 0
    for port in list:
        count = count + len(gpios[port])
    return count

layout_height_of_left_side_gpios = number_of_gpio_pins(left_side_gpios_from_bottom) * pin_label_layout_height + (len(left_side_gpios_from_bottom) - 1) * gpio_port_layout_margin

layout_min_height_of_left_side = layout_height_of_other_pin_list + left_side_layout_margin + layout_height_of_left_side_gpios + labels_sides_margin * 2

layout_min_height_of_right_side = number_of_gpio_pins(right_side_gpios_from_bottom) * pin_label_layout_height + (len(right_side_gpios_from_bottom) - 1) * gpio_port_layout_margin + labels_sides_margin * 2

layout_min_width_of_top_side = layout_height_of_power_pin_list + labels_sides_margin * 2 + max_left_right_label_length * character_layout_length
layout_min_width_of_bottom_side = layout_height_of_ground_pin_list + labels_sides_margin * 2 + 2 * max_left_right_label_length * character_layout_length

layout_height = max(layout_height_of_left_side_gpios, layout_min_height_of_right_side)
layout_width = max(layout_min_width_of_top_side, layout_min_width_of_bottom_side)

halfwidth = layout_width / 2
halfheight = layout_height / 2

vars["left"] = -(halfwidth)
vars["right"] = (halfwidth)
vars["top"] = halfheight
vars["bottom"] = -(halfheight)

pin_string = ""

pintype = {
    "Boot": "I",
    "MonoIO": "O",
    "Reset": "I",
    "Power": "W",
    "I/O": "B"
}

# Even though Y is positive going downwards in the status area in
# the component editor, it's actually positive going upwards.

X = - len(power) * pin_label_layout_height // 2
for p in power:
    pin_string += "X %s %s %d %d 200 D 50 50 1 1 %s\n" % (fixed_name(p["@Name"]), p["@Position"], X, halfheight + pin_layout_length, pintype[p['@Type']])
    X = X + pin_label_layout_height

vars["labelY"] = halfheight + 50
vars["labelX"] = X + pin_label_layout_height

X = - len(ground) * pin_label_layout_height // 2
for p in ground:
    pin_string += "X %s %s %d %d 200 U 50 50 1 1 %s\n" % (fixed_name(p["@Name"]), p["@Position"], X, -halfheight - pin_layout_length, pintype[p['@Type']])
    X = X + pin_label_layout_height

Y = - halfheight + labels_sides_margin
for p in other:
    pin_string += "X %s %s %d %d 200 R 50 50 1 1 %s\n" % (fixed_name(p["@Name"]), p["@Position"], -halfwidth - pin_layout_length, -Y, pintype[p['@Type']])
    Y = Y + pin_label_layout_height

Y = halfheight - labels_sides_margin
for g in left_side_gpios_from_bottom:
    for p in reversed(gpios[g]):
        pin_string += "X %s %s %d %d 200 R 50 50 1 1 %s\n" % (fixed_name(p["@Name"]), p["@Position"], -halfwidth - pin_layout_length, -Y, pintype[p['@Type']])
        Y = Y - pin_label_layout_height
    Y = Y - gpio_port_layout_margin

Y = halfheight - labels_sides_margin
for g in right_side_gpios_from_bottom:
    for p in reversed(gpios[g]):
        pin_string += "X %s %s %d %d 200 L 50 50 1 1 %s\n" % (fixed_name(p["@Name"]), p["@Position"], halfwidth + pin_layout_length, -Y, pintype[p['@Type']])
        Y = Y - pin_label_layout_height
    Y = Y - gpio_port_layout_margin

pro_guidance = """#
# Put this in your .pro file, adding "../" if necessary
# "LibName31=%(partname)s"
#"""

sch_guidance = """#
# Put this in your .sch file:"
# "LIBS:%(partname)s"
#"""

vars["pins"] = pin_string
libfile = open(partname + ".lib", "w")
libfile.write(lib_body % vars)
libfile.write(pro_guidance % vars)
libfile.write(sch_guidance % vars)
libfile.close()

dcmfile = open(partname + ".dcm", "w")
dcmfile.write(dcm_body % vars)
dcmfile.close()

print(pro_guidance % vars)
print(sch_guidance % vars)
