#!/usr/bin/env python3
"""Suppress the cargo-subtype text on articulated parts with zero capacity.

OpenTTD's vehicle details window adds an "N/A" line for every part that has
cargo_cap == 0 but still returns a cargo-subtype text (see
GetCargoSummaryOfArticulatedVehicle in train_gui.cpp).  China Set coaches are
3-part articulated; only the middle part has capacity, but the livery selector
(cargo_subtype_text) is defined for every part, which produced the extra line.

This rewrites each `switch (FEAT_TRAINS, SELF, switch_X_cargo_subtype,
cargo_subtype)` into a two-stage switch:

    switch (FEAT_TRAINS, SELF, switch_X_cargo_subtype, cargo_capacity) {
        0: return CB_RESULT_NO_TEXT;
        switch_X_cargo_subtype_livery;
    }
    switch (FEAT_TRAINS, SELF, switch_X_cargo_subtype_livery, cargo_subtype) {
        ...original body...
    }

Variable 0x3A (cargo_capacity) returns the *part's* capacity, so empty parts
now report no subtype text and are skipped by the details window, while the
livery names stay available for the part that actually carries cargo (and for
the purchase/refit menus).
"""
import os
import re
import sys

SWITCH_RE = re.compile(
    r"switch\s*\(\s*FEAT_TRAINS\s*,\s*SELF\s*,\s*(switch_[A-Za-z0-9_]*cargo_subtype)\s*,\s*cargo_subtype\s*\)\s*\{(.*?)\n\}",
    re.S,
)


def patch_file(path):
    src = open(path, encoding="utf-8", errors="surrogateescape").read()
    count = 0

    def repl(m):
        nonlocal count
        name, body = m.group(1), m.group(2)
        if name.endswith("_livery"):
            return m.group(0)
        count += 1
        # The livery switch must be defined before the guard that references it.
        return (
            f"switch (FEAT_TRAINS, SELF, {name}_livery, cargo_subtype) {{{body}\n}}\n"
            f"switch (FEAT_TRAINS, SELF, {name}, cargo_capacity) {{\n"
            f"    0: return CB_RESULT_NO_TEXT;\n"
            f"    {name}_livery;\n"
            f"}}"
        )

    out = SWITCH_RE.sub(repl, src)
    if count:
        open(path, "w", encoding="utf-8", errors="surrogateescape").write(out)
    return count


def main(base):
    total = 0
    files = 0
    for root, _, names in os.walk(os.path.join(base, "src")):
        for fn in names:
            if not fn.endswith(".pnml"):
                continue
            n = patch_file(os.path.join(root, fn))
            if n:
                total += n
                files += 1
    print(f"patched {total} cargo_subtype switches in {files} files")


if __name__ == "__main__":
    main(sys.argv[1])
