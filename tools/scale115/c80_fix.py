#!/usr/bin/env python3
"""Fix the C80 three-section hopper for the 1.15 rebuild.

The C80 is a 9-part articulated wagon: three sections of three parts, with the
section artwork drawn on the middle part.  At 1x each section is 2+2+2 = 6 units
long and its artwork is 6 units wide, so neighbouring sections exactly touch.

scale115.py only rewrites `switch_length_*` switches and other switches whose
name contains "length"; the C80 uses a literal `length: return 2;` and was
therefore never rescaled.  After the 1.15 re-render the section artwork is
6.75-6.9 units wide but the sections are still 6 units, so every joint
overlaps by ~0.8 units.

Fix: give the middle part of every section 3 units (2/3/2 = 7 units per
section, 21 units total instead of 18).  The front edge of each section (and
therefore the artwork anchor) does not move, and the joint becomes a ~0.2 unit
gap instead of an overlap.

Run AFTER scale115.py and subtype_fix.py.  Idempotent.
"""
import sys, os

SWITCH = """switch (FEAT_TRAINS, SELF, switch_c80_length, position_in_articulated_veh % 3) {
    1: return 3;
    return 2;
}
"""


def patch(path):
    s = open(path, encoding='utf-8', errors='surrogateescape').read()
    changed = False
    if 'switch_c80_length' not in s:
        s = s.replace('item (FEAT_TRAINS, c80) {',
                      SWITCH + '\nitem (FEAT_TRAINS, c80) {', 1)
        changed = True
    if 'length:                         return 2;' in s:
        s = s.replace('length:                         return 2;',
                      'length:                         switch_c80_length;', 1)
        changed = True
    if changed:
        open(path, 'w', encoding='utf-8', errors='surrogateescape').write(s)
    return changed


if __name__ == '__main__':
    base = sys.argv[1]
    p = os.path.join(base, 'src', 'wagons', 'c80.pnml')
    print('c80 patched' if patch(p) else 'c80 already patched')
