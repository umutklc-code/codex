# Deniz Hukuk Bürosu Backend

Bu depo, Deniz Hukuk Bürosu için geliştirilen FastAPI tabanlı bir arka uç uygulamasını içerir. API; avukat profilleri, uzmanlık alanları, dava sonuçları, müşteri geri bildirimleri ve iletişim mesajlarını yönetmek için uç noktalar sağlar.

## Özellikler

- Uzmanlık alanlarını listeleme ve yönetme
- Avukat profillerini oluşturma, güncelleme ve silme
- Başarı hikayeleri (dava sonuçları) kaydı
- Müşteri geri bildirimleri (referanslar) toplama
- İletişim formu mesajlarını kaydetme
- CORS yapılandırması sayesinde farklı ön yüzler tarafından kullanılabilir

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Geliştirme Sunucusunu Başlatma

```bash
uvicorn app.main:app --reload
```

Sunucu varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır. Etkileşimli API dokümantasyonuna `http://127.0.0.1:8000/docs` üzerinden erişebilirsiniz.

## Çevresel Değişkenler

- `DATABASE_URL`: Varsayılan olarak `sqlite:///./law_firm.db` kullanılır. İsteğe bağlı olarak PostgreSQL gibi farklı bir veritabanı URI'si tanımlanabilir.

## Test Verisi Oluşturma

Hızlıca denemek için `app/database.py` içerisindeki `session_scope` yardımcı fonksiyonu kullanılabilir:

```python
from app.database import session_scope
from app import models

with session_scope() as session:
    family_law = models.PracticeArea(name="Aile Hukuku", description="Boşanma, velayet ve miras.")
    session.add(family_law)
```

Bu arka uç üzerine inşa edeceğiniz ön yüz uygulaması, uç noktaları kullanarak içerik yönetimi yapabilir.
