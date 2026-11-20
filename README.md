# Tuval Cam — Resmî Web Sitesi

**Yayın:** https://www.tuvalcam.com/

Bu depo, daha önce https://tuvalcam.pages.dev/ adresinde yayımlanan Tuval Cam sitesinin HTML, CSS, JavaScript ve 16 galeri fotoğrafından aktarılmış hâlidir.

## GitHub Pages

Repository Settings → Pages → Build and deployment → Deploy from a branch → Branch: `main` ve `/(root)` → Save.

**Custom domain:** `www.tuvalcam.com` (kök dizindeki `CNAME`). DNS sağlayıcısındaki `www` CNAME kaydı `tuvalcam.github.io` hedefini göstermelidir. Kök alan adı `tuvalcam.com` istenirse GitHub Pages A kayıtlarıyla yönlendirilir.

Site statiktir; derleme komutu yoktur. `index.html` ana sayfadır. `cam/`, `ayna/`, `cerceve/`, `sineklik/` klasörleri doğrudan URL açılışlarını destekler. Ürün galerisi `photo-gallery.js` ve `photo-gallery.css` ile, görseller `assets/gallery/` ile sunulur. Teklif formu WhatsApp üzerinden açılır.

Eski Cloudflare Pages yayını GitHub Pages aktivasyonu ve DNS doğrulaması tamamlanana kadar korunmalıdır.
