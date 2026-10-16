"""Build the deployable site/ folder from trade-icons.html (no installs needed).

- Inlines every icon layer (icons/web, made by tools/optimize_icons.py) into the
  page as a cropped data URI, so the whole site is one fast request.
- Strips comments and indentation.
- Writes site/index.html and site/vercel.json.

Run from anywhere:  python3 tools/build_site.py
"""
import base64, gzip, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'trade-icons.html')
OUT = os.path.join(ROOT, 'site')

html = open(SRC, encoding='utf-8').read()
manifest = json.load(open(os.path.join(ROOT, 'icons', 'web', 'manifest.json')))

# 1) inline icon layers at their cropped position on the 60x60 canvas
def inline(m):
    attrs, href, extra = m.group(1), m.group(2), m.group(3)
    e = manifest[href]
    data = base64.b64encode(open(os.path.join(ROOT, e['file']), 'rb').read()).decode()
    return f'<image{attrs} href="data:{e["mime"]};base64,{data}" x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}"{extra}/>'

html, n = re.subn(r'<image((?: [a-z-]+="[^"]*")*?) href="(icons/layers/[^"]+\.png)" width="60" height="60"((?: [a-z-]+="[^"]*")*)/>', inline, html)
assert n == len(manifest), f'inlined {n} of {len(manifest)} layers'
assert not re.search(r'["\']icons/', html), 'a file reference to icons/ was left behind'

# 2) light minification: drop HTML comments and indentation
html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
html = '\n'.join(line.strip() for line in html.splitlines() if line.strip()) + '\n'

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

# 3) Vercel config: always revalidate the page, plus a couple of safe headers
vercel = {
    'headers': [{
        'source': '/(.*)',
        'headers': [
            {'key': 'Cache-Control', 'value': 'public, max-age=0, must-revalidate'},
            {'key': 'X-Content-Type-Options', 'value': 'nosniff'},
            {'key': 'Referrer-Policy', 'value': 'strict-origin-when-cross-origin'},
        ],
    }],
}
json.dump(vercel, open(os.path.join(OUT, 'vercel.json'), 'w'), indent=2)

raw = len(html.encode())
print(f'site/index.html: {raw / 1024:.0f} KB, about {len(gzip.compress(html.encode(), 9)) / 1024:.0f} KB over the wire ({n} icon layers inlined)')
