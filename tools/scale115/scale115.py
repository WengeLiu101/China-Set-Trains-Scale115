#!/usr/bin/env python3
"""Patch China Set NML for a uniform 1.15 render/length scale.

- template.pnml: remap every 4x sprite rect to the 1.15 sheet layout
- functions.pnml: rescale switch_length_* part lengths (total preserved)
- other *.pnml: rescale any other switch whose name contains 'length'
"""
import os, re, sys, math

K = 1.15
OLD_X = {0:0, 44:1, 172:2, 372:3, 500:4, 544:5, 672:6, 872:7}
WS = [36,120,192,120,36,120,192,120]
HS = [166,116,80,116,166,116,80,116]
# exact layout as gorender: x += int(float64(w+8)*scale)
NEW_X, NEW_W, NEW_H = [], [], []
w = 0
for W, H in zip(WS, HS):
    NEW_X.append(w)
    NEW_W.append(int(W * K))
    NEW_H.append(int(H * K))
    w += int(float(W + 8) * K)

rect_re = re.compile(r'\[\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(.+?)\s*\]')

def scale_templates(path):
    out = []
    for line in open(path, encoding='utf-8', errors='surrogateescape'):
        m = rect_re.search(line)
        if m and '_32bpp.png' in m.group(7):
            x, y, w0, h0, ox, oy = map(int, m.groups()[:6])
            view = OLD_X.get(x)
            if view is not None:
                nx, nw, nh = NEW_X[view], NEW_W[view], NEW_H[view]
            elif x == 856:
                # gfx/steam/extralength sheet: widths 36,160,256,...; view 6
                nx, nw, nh = 982, 294, 92
            else:
                nx, nw, nh = round(x*K), round(w0*K), round(h0*K)
            nox = round(ox*K)
            noy = round(oy*K)  # uniform scale about the sprite origin
            new = f'[{nx:4d}, {y:3d}, {nw:4d}, {nh:3d}, {nox:4d}, {noy:4d}, {m.group(7)}]'
            line = line[:m.start()] + new + line[m.end():]
        out.append(line)
    open(path, 'w', encoding='utf-8', errors='surrogateescape').write(''.join(out))
    print('templates patched:', path)

switch_re = re.compile(r'switch\s*\(\s*[^,]+,\s*[^,]+,\s*([A-Za-z0-9_]+)\s*,(.*?)\)\s*\{(.*?)\n\s*\}', re.S)
ret_re = re.compile(r'return\s+(\d+)\s*;')

def rescale_two(e, m):
    # switch returns (end, middle); parts are e, m, e
    T = round((2 * e + m) * K)
    m2 = min(8, max(1, round(m * K)))
    e2 = max(1, min(8, round((T - m2) / 2)))
    return e2, m2

def patch_length_switches(src_dir):
    fpath = os.path.join(src_dir, 'functions.pnml')
    s = open(fpath, encoding='utf-8', errors='surrogateescape').read()
    def repl(m):
        name, body = m.group(1), m.group(3)
        if 'switch_length_' not in name:
            return m.group(0)
        rets = [int(x) for x in ret_re.findall(body)]
        if len(rets) == 2:
            # text order: 1: <middle>;  return <end>  -> positions (end, mid, end)
            mid0, end0 = rets[0], rets[1]
            vals = [end0, mid0, end0]
        elif len(rets) == 3:
            vals = rets
        else:
            return m.group(0)
        # Front part length: identical for every vehicle type so the art
        # offsets cancel inside the set.  Must match the China Set default
        # (build h, front = 2) so that metro/MTR cars couple to China cars
        # with the same joint spacing.
        front = 2
        art = sum(vals) * K
        # Half-up rounding: a hair of air between cars reads better than an
        # overlap ("squeezed together").  Shifting T down by one unit (the old
        # rule) left types like 2_6_2 (art 11.5) at T=11, i.e. 8 px of
        # interpenetration per joint at 4x.
        T = int(math.floor(art + 0.5))
        # If rounding still leaves a visible squeeze, round up instead.
        if T - art < -0.3:
            T += 1
        # Each articulated part is at most 8 units long; front is frozen.
        T = min(T, front + 16)
        # Keep the FRONT part length unchanged: the art is anchored at the
        # middle part's front, so all vehicles must share the same front
        # length for the offsets to cancel across a joint.
        mid = min(8, max(1, T - front - 1))
        rear = T - front - mid
        if rear > 8:
            rear = 8
            mid = T - front - rear
        if rear < 1:
            rear = 1
            mid = T - front - 1
        if mid < 1:
            mid = 1
            rear = T - front - 1
        rear = max(1, min(8, rear))
        nl = "\n"
        return (f'switch (FEAT_TRAINS, SELF, {name}, position_in_articulated_veh % 3) {{{nl}'
                f'    0: return {front};{nl}'
                f'    1: return {mid};{nl}'
                f'    2: return {rear};{nl}'
                f'}}')
    s2, n = switch_re.subn(repl, s)
    open(fpath, 'w', encoding='utf-8', errors='surrogateescape').write(s2)
    print('generic length switches patched:', n)

def patch_other_lengths(src_dir):
    total = 0
    for root, dirs, files in os.walk(src_dir):
        for fn in files:
            if not fn.endswith('.pnml'): continue
            p = os.path.join(root, fn)
            if os.path.abspath(p) == os.path.abspath(os.path.join(src_dir, 'functions.pnml')): continue
            s = open(p, encoding='utf-8', errors='surrogateescape').read()
            if 'switch' not in s: continue
            def repl(m):
                nonlocal total
                name, body = m.group(1), m.group(3)
                if 'length' not in name.lower(): return m.group(0)
                rets = ret_re.findall(body)
                if not rets: return m.group(0)
                # scale each part individually (cap 8)
                it = iter([max(1, min(8, round(int(x)*K))) for x in rets])
                body2 = ret_re.sub(lambda mm: f'return {next(it)};', body)
                total += 1
                return m.group(0).replace(body, body2)
            s2 = switch_re.sub(repl, s)
            if s2 != s:
                open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s2)
    print('custom length switches patched:', total)

if __name__ == '__main__':
    base = sys.argv[1]
    scale_templates(os.path.join(base, 'src', 'template.pnml'))
    patch_length_switches(os.path.join(base, 'src'))
    patch_other_lengths(os.path.join(base, 'src'))
    print('NEW layout x', NEW_X, 'w', NEW_W, 'h', NEW_H)
