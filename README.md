# Okul Öncesi Oyunlar

Akıllı tahta için hazırlanmış okul öncesi oyunları: harf, ses, dikkat, bellek ve çizgi çalışmaları.

**Oyna:** https://eyupcalskanozturk-tr.github.io/okul-oncesi-oyunlar/

## Oyunlar

| Oyun | Ne yapılıyor | Odak |
|---|---|---|
| Mandallı Kelimeler | Kelimenin harflerini mandallardan bulup sırayla takma | Harf tanıma, sıralama |
| Harf Avcıları | Harfli balonları patlatma, sayılılara dokunmama; tekerleme ekranı | Harf–rakam ayırt etme, dikkat |
| Ahtapot | Resimleri ilk sesine göre doğru ahtapotun koluna yerleştirme | İlk ses farkındalığı |
| Hafıza Bavulu | "Ben tatile gidiyorum ve yanıma … alıyorum" zinciri | Sıralı bellek, dinleme |
| Çizgi Takibi | Desenlerin üzerinden geçme ve boyama; tahta 1, 2 ya da 4 çocuğa bölünür | İnce motor, yazıya hazırlık |

- Kurulum gerekmez; Windows, Mac, iPad ve akıllı tahtada tarayıcıda açılır.
- Web adresi bir kez açıldıktan sonra oyunlar internetsiz de çalışır. Tablette "Ana Ekrana Ekle" ile uygulama gibi açılır.
- Türkçe seslendirme cihazın kendi sesini kullanır (Windows'ta Edge ile "Emel", Mac ve iPad'de "Yelda").
- Skorlar ve ayarlar oyunu açan cihazın tarayıcısında saklanır; hiçbir veri dışarı gönderilmez.

## Klasörler

- `docs/`: Yayınlanan site (GitHub Pages bu klasörden yayınlar). Elle düzenlenmez, `kaynak/build.py` üretir.
- `kaynak/harf/harf-avcilari.html`: İlk dört oyunun ortak kaynağı.
- `kaynak/cizgi/cizgi.html`: Çizgi Takibi'nin kaynağı.
- `kaynak/hub/`: Oyun listesi sayfası, ekran görüntüleri ve uygulama simgesi.
- `kaynak/fonts/`: Gömülü yazı tipleri (Türkçe harfler eklenmiş Fredoka ve Andika).

## Güncelleme

```sh
python3 kaynak/build.py          # docs/ klasörünü yeniden üretir
python3 kaynak/build.py --zip    # ayrıca build/okul-oncesi-oyunlar.zip (internetsiz paket)
```

Sonra değişiklikleri commit edip gönderin; site bir iki dakikada güncellenir. Yalnızca Python 3 gerekir.
Simgeyi değiştirmek için `kaynak/hub/icon.svg` düzenlenip `python3 kaynak/hub/make_icons.py` çalıştırılır (Playwright gerekir).

## Yazı tipleri

[Fredoka](https://fonts.google.com/specimen/Fredoka) ve [Andika](https://software.sil.org/andika/) yazı tipleri [SIL Open Font License 1.1](https://openfontlicense.org) ile lisanslıdır.
