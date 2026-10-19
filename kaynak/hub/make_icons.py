"""Uygulama simgelerini kaynak/hub/icon.svg'den üretir (docs/icons/). Gerekli: pip install playwright && playwright install chromium"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'kaynak'))
from fonts.fontcss import font_css
from playwright.sync_api import sync_playwright
svg = open(os.path.join(ROOT, 'kaynak/hub/icon.svg'), encoding='utf-8').read()
defs = re.search(r'<defs>.*?</defs>', svg, re.S).group(0)
bg = re.search(r'<g id="bg">.*?</g>', svg, re.S).group(0)
fg = re.search(r'<g id="fg">.*?</g>', svg, re.S).group(0)
def doc(size, mode):
    if mode == 'mask': art = bg + '<g transform="translate(51.2 51.2) scale(.8)">' + fg + '</g>'
    else: art = bg + fg
    if mode == 'any': art = '<clipPath id="r"><rect width="512" height="512" rx="112"/></clipPath><g clip-path="url(#r)">' + art + '</g>'
    return (f'<!doctype html><html><head><style>{font_css()} html,body{{margin:0;background:transparent}}</style></head><body>'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="{size}" height="{size}">{defs}{art}</svg></body></html>')
out = os.path.join(ROOT, 'docs/icons'); os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, size, mode in [('icon-192.png', 192, 'any'), ('icon-512.png', 512, 'any'), ('maskable-512.png', 512, 'mask'), ('apple-touch-icon.png', 180, 'full'), ('favicon-32.png', 32, 'any')]:
        pg = b.new_page(viewport={'width': size, 'height': size}); pg.set_content(doc(size, mode)); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(out, name), omit_background=(mode == 'any')); pg.close()
    b.close()
print('simgeler hazır:', out)
