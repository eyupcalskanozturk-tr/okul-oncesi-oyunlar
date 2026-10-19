"""Yazı tiplerini base64 @font-face olarak üretir. Fredoka'ya eksik Türkçe harfler (Ğ ğ İ Ş ş) eklenmiş sürümdür."""
import base64, os
HERE = os.path.dirname(os.path.abspath(__file__))
def _b(f): return base64.b64encode(open(os.path.join(HERE, f), 'rb').read()).decode()
def font_css():
    return ("/* Yazı tipleri dosyanın içinde: internet olmadan da aynı görünür. Fredoka'ya eksik Türkçe harfler (Ğ ğ İ Ş ş) eklendi. */\n"
        "@font-face{font-family:'Fredoka';src:url(data:font/woff2;base64," + _b('fredoka-tr.woff2') + ") format('woff2');font-weight:300 700;font-style:normal;font-display:block}\n"
        "@font-face{font-family:'Andika';src:url(data:font/woff2;base64," + _b('andika-400.woff2') + ") format('woff2');font-weight:400;font-style:normal;font-display:block}\n"
        "@font-face{font-family:'Andika';src:url(data:font/woff2;base64," + _b('andika-700.woff2') + ") format('woff2');font-weight:700;font-style:normal;font-display:block}")
