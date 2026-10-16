"""One-time icon optimisation (needs Pillow): crop every layer in icons/layers to
its painted area, save it as an optimised PNG, and write icons/web/manifest.json
with each crop's position on the 60x60 canvas. (PNG rather than WebP: browsers
decode WebP with premultiplied alpha, which shifts faint edge pixels slightly;
PNG keeps the artwork pixel-exact for ~15 KB more.)
tools/build_site.py then inlines these into the deployable page."""
import io, json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'icons', 'layers')
OUT = os.path.join(ROOT, 'icons', 'web')

manifest = {}
before = after = 0
for icon in sorted(os.listdir(SRC)):
    for f in sorted(os.listdir(os.path.join(SRC, icon))):
        if not f.endswith('.png'):
            continue
        path = os.path.join(SRC, icon, f)
        before += os.path.getsize(path)
        im = Image.open(path).convert('RGBA')
        x0, y0, x1, y1 = im.getchannel('A').getbbox()
        crop = im.crop((x0, y0, x1, y1))
        png = io.BytesIO(); crop.save(png, 'PNG', optimize=True)
        data, ext, mime = png.getvalue(), 'png', 'image/png'
        # lossless check: decoded crop must match the original pixels exactly
        assert Image.open(io.BytesIO(data)).convert('RGBA').tobytes() == crop.tobytes(), path
        rel = f'{icon}/{f[:-4]}.{ext}'
        os.makedirs(os.path.join(OUT, icon), exist_ok=True)
        open(os.path.join(OUT, rel), 'wb').write(data)
        after += len(data)
        manifest[f'icons/layers/{icon}/{f}'] = {'file': f'icons/web/{rel}', 'mime': mime, 'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0}

json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print(f'{len(manifest)} layers: {before} -> {after} bytes ({100 * after / before:.0f}%)')
