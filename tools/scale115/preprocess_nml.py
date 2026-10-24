#!/usr/bin/env python3
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(sys.argv[1]))
MAIN = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
macros = {
    'REPO_REVISION': '1000',
    'MIN_COMPATIBLE_VERSION': '0',
    'VERSION_STRING': '0.4.2-scale115',
}
inc_re = re.compile(r'^\s*#include\s+"([^"]+)"')
def_re = re.compile(r'^\s*#define\s+(\w+)\s*(.*)$')

def subst(line):
    for k in sorted(macros, key=len, reverse=True):
        line = re.sub(r'\b' + re.escape(k) + r'\b', macros[k], line)
    return line

def process(path, out, seen):
    path = os.path.abspath(path)
    if path in seen:
        # still emit? avoid double include loops
        return
    seen.add(path)
    with open(path, encoding='utf-8', errors='surrogateescape') as f:
        for line in f:
            m = inc_re.match(line)
            if m:
                inc = os.path.join(os.path.dirname(path), m.group(1))
                process(inc, out, seen)
                continue
            m = def_re.match(line)
            if m:
                name, val = m.group(1), m.group(2).strip()
                if val:
                    macros[name] = val
                out.write('\n')
                continue
            out.write(subst(line))

with open(OUT, 'w', encoding='utf-8', errors='surrogateescape') as out:
    process(MAIN, out, set())
print('wrote', OUT, 'macros', len(macros))
