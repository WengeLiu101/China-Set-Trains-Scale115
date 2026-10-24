#!/usr/bin/env python3
"""Render every China Set .vox at 1.15x with renderobject."""
import os, subprocess, sys, concurrent.futures as cf

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
TOOL = os.environ.get('RENDEROBJECT') or os.path.abspath(os.path.join(ROOT, 'tools', 'renderobject.exe'))

SCALE = '1.15'

def jobs():
    for dirpath, _, files in os.walk(os.path.join(ROOT, 'gfx')):
        manifest = os.path.join(dirpath, 'manifest.json')
        if not os.path.exists(manifest):
            continue
        for fn in files:
            if not fn.lower().endswith('.vox'):
                continue
            vox = os.path.join(dirpath, fn)
            out = os.path.join(dirpath, fn[:-4] + '_32bpp.png')
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(vox):
                continue
            pal = os.path.join(dirpath, 'ttd_palette.json')
            d = dirpath
            while not os.path.exists(pal) and os.path.dirname(d) != d:
                d = os.path.dirname(d)
                pal = os.path.join(d, 'ttd_palette.json')
            if not os.path.exists(pal): pal = os.path.join(ROOT, 'ttd_palette.json')
            yield manifest, vox, out, pal

def run(job):
    manifest, vox, out, pal = job
    cmd = [TOOL, '-m', manifest, '--palette', pal, '-scale', SCALE, vox]
    r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode != 0 or not os.path.exists(out):
        return (vox, r.returncode)
    return None

if __name__ == '__main__':
    all_jobs = list(jobs())
    print('models to render:', len(all_jobs), flush=True)
    fails = []
    with cf.ProcessPoolExecutor(max_workers=8) as ex:
        for i, res in enumerate(ex.map(run, all_jobs), 1):
            if res: fails.append(res)
            if i % 25 == 0: print(f'{i}/{len(all_jobs)} done, fails={len(fails)}', flush=True)
    print('FAILS', len(fails))
    for f in fails[:20]: print(f)
