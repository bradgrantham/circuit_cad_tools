# circuit_cad_tools
CAD tools for making circuits and PCBs

Here's a handful of tools for easing the production of designs and PCBs (using KiCAD for now)

coalese_kicad_bom.py - take the output of the BOM button in KiCAD eeschema and output a BOM with unique parts combined.

kicad_to_digikey_bom.py - take the output of the BOM button in KiCAD eeschemagenerate a DigiKey BOM (probably needing massaging before input to DigiKey)

make_kicad4_component.py - Make a KiCAD component from a somewhat esoteric input format with pins and pin direction

kyocera_6288.generate_kicad4_footprint.py and microsd_1040310811.generate_kicad4_footprint.py - Generate a KiCAD footprint made of rectangles programatically.  (i.e. have the datasheet in front of you with measurements and you can write the script to output a footprint matching those measurements)  Two examples can be massaged into a new example (need to make a Python module)
