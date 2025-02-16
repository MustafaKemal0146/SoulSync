# SoulSync - Müzik Duygu Analizi

SoulSync, şarkı sözlerini analiz ederek duygusal içeriğini değerlendiren bir terminal uygulamasıdır. Yapay zeka kullanarak şarkıların duygusal yoğunluğunu ölçer ve beş temel duygu kategorisinde skorlar üretir.

## Özellikler

- 🎵 Şarkı sözleri otomatik arama ve çekme
- 🤖 Yapay zeka tabanlı duygu analizi
- 📊 5 farklı duygu kategorisinde değerlendirme:
  - Mutluluk
  - Hüzün
  - Öfke
  - Korku
  - Aşk
- 📝 Analiz sonuçlarını dosyaya kaydetme
- 🎨 Renkli ve interaktif terminal arayüzü
- 📋 Detaylı işlem logları

## Kurulum

1. Repo'yu klonlayın:
```bash
git clone https://github.com/mustafakemal0146/soulsync.git
cd soulsync
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. API anahtarlarını alın:
   - Genius API: [Genius API](https://genius.com/api-clients)
   - Groq API: [Groq AI](https://groq.com)

4. `.env` dosyası ayarlayın:
```env
GENIUS_API_KEY=your_genius_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Kullanım

1. Programı çalıştırın:
```bash
python main.py
```

2. Menüden "Şarkı Analizi" seçeneğini seçin
3. Şarkı adı ve sanatçı bilgilerini girin
4. Analiz sonuçlarını terminal ekranında görüntüleyin
5. Sonuçlar otomatik olarak txt dosyasına kaydedilecektir

## API Gereksinimleri

### Genius API
- Şarkı sözlerini çekmek için kullanılır
- [Genius API Docs](https://docs.genius.com)
- Ücretsiz hesap ile kullanılabilir
- Rate limit: 5000 istek/saat

### Groq API
- Duygu analizi için kullanılır
- [Groq AI Docs](https://groq.com/docs)
- Ücretsiz deneme sürümü mevcuttur
- Hızlı ve doğru sonuçlar

## Örnek Çıktı

```
==================================================
Şarkı Analizi: Nilüfer - Müslüm Gürses
==================================================

Duygusal Analiz:
Mutluluk: 10.0%
Hüzün: 85.5%
Öfke: 15.2%
Korku: 5.3%
Aşk: 90.2%

Baskın Duygu: Aşk
Analiz Özeti: Bu şarkı ağırlıklı olarak aşk duygusunu ifade ediyor.
```

## Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit'leyin (`git commit -m 'feat: add amazing feature'`)
4. Branch'e push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## İletişim

Mustafa Kemal Çıngıl

- LinkedIn: [Mustafa Kemal Çıngıl](https://www.linkedin.com/in/mustafakemalcingil/)
- GitHub: [@mustafakemal0146](https://github.com/mustafakemal0146)
- Email: mustafakemal0146@gmail.com

Proje Linki: [https://github.com/mustafakemal0146/soulsync](https://github.com/mustafakemal0146/soulsync)

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
