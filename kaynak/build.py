"""Oyunları ve oyun listesi sayfasını kaynak/ klasöründen üretir.

Kullanım (repo kökünde):
    python3 kaynak/build.py            -> docs/ (GitHub Pages sitesi)
    python3 kaynak/build.py --zip      -> ayrıca build/okul-oncesi-oyunlar.zip
    python3 kaynak/build.py --claude   -> ayrıca build/claude/ (Claude sayfası biçimi, <html> sarmalayıcısı yok)

Yalnızca Python 3 standart kütüphanesi gerekir.
"""
import base64, datetime, hashlib, json, os, re, shutil, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(ROOT, 'kaynak')
DOCS = os.path.join(ROOT, 'docs')
BUILD = os.path.join(ROOT, 'build')
sys.path.insert(0, K)
from fonts.fontcss import font_css  # noqa: E402

SITE_URL = 'https://eyupcalskanozturk-tr.github.io/okul-oncesi-oyunlar/'
FONTS = font_css()
HARF_SRC = open(os.path.join(K, 'harf', 'harf-avcilari.html'), encoding='utf-8').read()

# Harf Avcıları kaynağından üretilen dört oyun
EDITIONS = [
    dict(slug='mandalli-kelimeler', cfg=dict(id='mandal', title='Mandallı Kelimeler', ls='mandalli-kelimeler', main='mandal', lesson='e9', csv='mandalli-kelimeler', rhyme=False)),
    dict(slug='harf-avcilari', cfg=dict(id='harf', title='Harf Avcıları', ls='harf-avcilari', main='balon', lesson='l1', csv='harf-avcilari', rhyme=True)),
    dict(slug='ahtapot', cfg=dict(id='ahtapot', title='Ahtapot', ls='ahtapot-oyunu', main='ahtapot', lesson='a1', csv='ahtapot', rhyme=False)),
    dict(slug='hafiza-bavulu', cfg=dict(id='bavul', title='Dijital Hafıza Bavulu', ls='hafiza-bavulu', main='bavul', lesson='b1', csv='hafiza-bavulu', rhyme=False)),
]

# Oyun listesi sayfasındaki kartlar
HUB_GAMES = [
    ('mandalli-kelimeler', 'Mandallı Kelimeler', 'Kartta yazan kelimenin harflerini mandallardan bul, kelimenin altına soldan sağa sırayla tak.', ['Harf tanıma', 'Soldan sağa sıralama', 'Kelimeyi harflerine ayırma']),
    ('harf-avcilari', 'Harf Avcıları', 'Gökyüzündeki balonlardan istenenleri patlat: ilk bölümde harfliler patlatılır, sayılılara dokunulmaz. Tekerleme ekranı da var.', ['Harf–rakam ayırt etme', 'Seçici dikkat', 'Tekerleme']),
    ('ahtapot', 'Ahtapot', 'Resimleri adının ilk sesine göre doğru ahtapotun kollarına yerleştir (örneğin K ve T sesi).', ['İlk ses farkındalığı', 'Sesleri ayırt etme', 'Sözcük dağarcığı']),
    ('hafiza-bavulu', 'Hafıza Bavulu', '“Ben tatile gidiyorum ve yanıma … alıyorum.” Her çocuk zincire bir eşya ekler, sonunda bavul sırayla kontrol edilir.', ['Sıralı bellek', 'Dinleme', 'Cümle kurma']),
    ('cizgi-takibi', 'Çizgi Takibi', 'Düz, zikzak, dalgalı, sarmal ve iç içe şekillerin üzerinden fırça ya da süngerle geç, sonra boya. Tahta 1, 2 ya da 4 çocuğa bölünür.', ['İnce motor', 'Göz–el koordinasyonu', 'Yazıya hazırlık']),
]

GAME_HEAD = ('<meta name="theme-color" content="#59B4EC">\n'
             '<link rel="icon" href="../icons/favicon-32.png" sizes="32x32" type="image/png">\n'
             '<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">\n')
GAME_SW = ("<script>if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) "
           "navigator.serviceWorker.register('../sw.js').catch(function () {});</script>\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def standalone(s):
    """Claude biçimindeki sayfayı tek başına açılan tam HTML belgesine çevirir."""
    i = s.index('</style>') + len('</style>')
    head, body = s[:i], s[i:]
    return ('<!DOCTYPE html>\n<html lang="tr">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">\n'
            + GAME_HEAD + head + '\n</head>\n<body>\n' + body.strip() + '\n' + GAME_SW + '</body>\n</html>\n')


def lower_tr(t):
    return t.replace('I', 'ı').replace('İ', 'i').lower()


def lesson_words(src, lesson_id):
    m = re.search(r"\{ id: '" + lesson_id + r"', .*?words: (.*?), prompts:", src, re.S)
    w = m.group(1)
    for arr in ('E9_WORDS', 'DEFAULT_WORDS', 'A1_WORDS', 'BAVUL_DEFAULT'):
        if w.startswith(arr):
            break
    else:
        sys.exit('bilinmeyen kelime listesi: ' + w[:40])
    lst = re.search(r'const ' + arr + r' = \[(.*?)\];', src, re.S).group(1)
    return [lower_tr(x) for x in re.findall(r"'([^']+)'", lst)]


def build_harf():
    """Harf Avcıları kaynağından dört oyunu üretir; her oyuna yalnızca kendi resimlerini koyar."""
    assert '/*@@FONTS@@*/' in HARF_SRC
    src = HARF_SRC.replace('/*@@FONTS@@*/', FONTS, 1)
    rm = re.search(r'const RASTER = \{\n(.*?)\n\};\n', src, re.S)
    entries = re.findall(r'^  ("(?:[^"\\]|\\.)*"): ("data:[^"]+")', rm.group(1), re.M)
    out = {}
    for ed in EDITIONS:
        cfg = ed['cfg']
        words = set(lesson_words(src, cfg['lesson']))
        keep = [f'  {k}: {v}' for k, v in entries
                if json.loads(k) in words or (cfg['main'] == 'ahtapot' and json.loads(k).startswith('__octo'))]
        s = src[:rm.start()] + 'const RASTER = {\n' + ',\n'.join(keep) + '\n};\n' + src[rm.end():]
        js = '{ ' + ', '.join(f"{k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v, bool) else str(v).lower()}" for k, v in cfg.items()) + ' }'
        s = re.sub(r'/\*EDITION\*/.*?/\*EDITION_END\*/', '/*EDITION*/' + js.replace('\\', '\\\\') + '/*EDITION_END*/', s, count=1)
        s = s.replace('<title>Harf Avcıları</title>', f"<title>{cfg['title']}</title>", 1)
        s = s.replace('<h1 id="homeTitle">Harf Avcıları</h1>', f'<h1 id="homeTitle">{cfg["title"]}</h1>', 1)
        out[ed['slug']] = s
    return out


def build_cizgi():
    """Çizgi Takibi'ni üretir; ses ve seslendirme kodunu Harf Avcıları kaynağından alır."""
    a = HARF_SRC.index('const audio = (() => {')
    b = HARF_SRC.index('/* =========================================================\n   Çizimler')
    audio = HARF_SRC[a:b].rstrip() + '\n'
    seg = HARF_SRC[HARF_SRC.index('const TTS_TEST = '):]
    voice = seg[:seg.index('\n}\n', seg.index('function mountVoiceRow')) + 3]
    c = open(os.path.join(K, 'cizgi', 'cizgi.html'), encoding='utf-8').read()
    assert '/*@@SHARED_AUDIO@@*/' in c and '/*@@SHARED_VOICE@@*/' in c
    c = c.replace('/*@@FONTS@@*/', FONTS, 1).replace('/*@@SHARED_AUDIO@@*/', audio).replace('/*@@SHARED_VOICE@@*/', voice)
    return {'cizgi-takibi': c}


def build_hub():
    arrow = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M6 3.5v13l10-6.5z" fill="currentColor"/></svg>'
    cards = []
    for slug, name, desc, tags in HUB_GAMES:
        img = base64.b64encode(open(os.path.join(K, 'hub', 'shots', slug + '.webp'), 'rb').read()).decode()
        href = f'oyunlar/{slug}.html'
        cards.append(
            f'<li class="game"><a class="shot" href="{href}" tabindex="-1" aria-hidden="true"><img src="data:image/webp;base64,{img}" alt="" width="800" height="450" loading="lazy"></a>'
            f'<div class="gbody"><h3>{name}</h3><p>{desc}</p><ul class="tags">' + ''.join(f'<li>{t}</li>' for t in tags)
            + f'</ul><a class="play" href="{href}" aria-label="{name} oyununu aç">{arrow}Oyna</a></div></li>')
    s = open(os.path.join(K, 'hub', 'index.html'), encoding='utf-8').read()
    months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    d = datetime.date.today()
    s = (s.replace('/*@@FONTS@@*/', FONTS, 1)
          .replace('<!--@@GAMES@@-->', '\n    '.join(cards), 1)
          .replace('<!--@@DATE@@-->', f'{d.day} {months[d.month - 1]} {d.year}', 1))
    return s


MANIFEST = {
    'name': 'Okul Öncesi Oyunlar',
    'short_name': 'Oyunlar',
    'description': 'Akıllı tahta için okul öncesi oyunları: harf, ses, bellek ve çizgi takibi.',
    'lang': 'tr',
    'dir': 'ltr',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'orientation': 'landscape',
    'background_color': '#EEF6EC',
    'theme_color': '#59B4EC',
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
        {'src': 'icons/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ],
}

SW = r"""/* Okul Öncesi Oyunlar: çevrimdışı çalışma.
   Sayfalar önce internetten alınır (en yeni sürüm), internet yoksa cihazdaki kopya açılır. */
const VERSION = '@@VERSION@@';
const CACHE = 'oyunlar-' + VERSION;
const FILES = @@FILES@@;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('oyunlar-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function fromNetwork(req, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('zaman aşımı')), ms);
    fetch(req).then(res => {
      clearTimeout(t);
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      resolve(res);
    }, err => { clearTimeout(t); reject(err); });
  });
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  const page = req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
  if (page) {
    e.respondWith(caches.match(req, { ignoreSearch: true }).then(cached =>
      fromNetwork(req, cached ? 4000 : 30000).catch(() => cached || caches.match('./'))));
  } else {
    e.respondWith(caches.match(req, { ignoreSearch: true }).then(cached => cached || fetch(req)));
  }
});
"""


def main():
    games = {**build_harf(), **build_cizgi()}
    # docs/ (site)
    if os.path.isdir(os.path.join(DOCS, 'oyunlar')):
        shutil.rmtree(os.path.join(DOCS, 'oyunlar'))
    for slug, s in games.items():
        write(os.path.join(DOCS, 'oyunlar', slug + '.html'), standalone(s))
    write(os.path.join(DOCS, 'index.html'), build_hub())
    write(os.path.join(DOCS, 'manifest.webmanifest'), json.dumps(MANIFEST, ensure_ascii=False, indent=2) + '\n')
    write(os.path.join(DOCS, '.nojekyll'), '')
    files = ['./', 'index.html', 'manifest.webmanifest'] + sorted('icons/' + f for f in os.listdir(os.path.join(DOCS, 'icons'))) \
        + [f'oyunlar/{slug}.html' for slug in games]
    h = hashlib.sha256()
    for f in files[1:]:
        h.update(open(os.path.join(DOCS, f), 'rb').read())
    write(os.path.join(DOCS, 'sw.js'), SW.replace('@@VERSION@@', h.hexdigest()[:12]).replace('@@FILES@@', json.dumps(files, indent=2)))
    print('docs/ hazır:', ', '.join(games), '| sürüm', h.hexdigest()[:12])

    if '--claude' in sys.argv:
        for slug, s in games.items():
            write(os.path.join(BUILD, 'claude', slug + '.html'), s)
        print('build/claude/ hazır')

    if '--zip' in sys.argv:
        os.makedirs(BUILD, exist_ok=True)
        readme = open(os.path.join(K, 'OKU-BENI.txt'), encoding='utf-8').read().replace('@@SITE@@', SITE_URL)
        zpath = os.path.join(BUILD, 'okul-oncesi-oyunlar.zip')
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.writestr('okul-oncesi-oyunlar/OKU-BENI.txt', ('﻿' + readme.replace('\n', '\r\n')).encode('utf-8'))
            for f in ['index.html', 'manifest.webmanifest'] + sorted('icons/' + f for f in os.listdir(os.path.join(DOCS, 'icons'))) \
                    + [f'oyunlar/{slug}.html' for slug in games]:
                z.write(os.path.join(DOCS, f), 'okul-oncesi-oyunlar/' + f)
        print('zip hazır:', zpath)


if __name__ == '__main__':
    main()
