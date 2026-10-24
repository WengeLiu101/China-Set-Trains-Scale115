# 1.15x scale rebuild tools

These scripts convert this set from the default OpenTTD scale to the 1.15x
scale used by the GETS train set, at the source level (not by resampling the
compiled GRF).

Build order (run from the repository root):

```sh
# 1. re-render every .vox at 1.15x (needs gorender's renderobject binary)
RENDEROBJECT=/path/to/renderobject python tools/scale115/render.py .
#    -> writes gfx/**/**_32bpp.png (git-ignored)

# 2. rescale the 4x sprite template rectangles and all articulated lengths
python tools/scale115/scale115.py .

# 3. suppress the extra "N/A" cargo-subtype line on empty articulated parts
python tools/scale115/subtype_fix.py .

# 4. C80 three-section hopper: 2/3/2 per section instead of 2/2/2
python tools/scale115/c80_fix.py .

# 5. preprocess + compile
python tools/scale115/preprocess_nml.py build115.nml chinasettrains.nml
nmlc chinasettrains.nml -o china115.grf -t custom_tags.txt
```

**Do not pass `-c` to nmlc.** Cropping transparent borders also shifts the
sprite offsets; with 32bpp sprites it leaves visible gaps between vehicle
sections (measured: the GRF is ~2.3 MB smaller and every C80 section drifts
apart).

All scripts are idempotent except `render.py` (which only re-renders when the
.vox is newer than the .png) and `scale115.py` (which must run on the pristine
upstream template; running it twice would scale twice).

License: GPL v2, same as the set.
