# Qaydnoma Backend — Django REST API

**Qaydnoma** — maqolalar, kategoriyalar, izohlar va foydalanuvchi autentifikatsiyasini boshqarish uchun mo'ljallangan to'liq funksional Django REST API backend tizimi.

---

## Mundarija

- [Loyiha haqida](#loyiha-haqida)
- [Ishlatilgan texnologiyalar](#ishlatilgan-texnologiyalar)
- [Loyiha tuzilmasi](#loyiha-tuzilmasi)
- [Ma'lumotlar bazasi modellari](#malumotlar-bazasi-modellari)
- [API endpointlari](#api-endpointlari)
- [Autentifikatsiya](#autentifikatsiya)
- [O'rnatish va ishga tushirish](#ornatish-va-ishga-tushirish)
- [Muhit o'zgaruvchilari](#muhit-ozgaruvchilari)
- [Deploy qilish](#deploy-qilish)

---

## Loyiha haqida

Qaydnoma — [qaydnomauz.uz](https://qaydnomauz.uz) domenida joylashgan o'zbek tilidagi kontent nashr platformasining backend qismi. Tizim maqolalar, kategoriyalar, izohlar va foydalanuvchi hisoblarini boshqaradi. Barcha ma'lumotlar RESTful API orqali taqdim etiladi.

**Asosiy imkoniyatlar:**

- Maqolalar va kategoriyalar boshqaruvi
- JWT asosidagi foydalanuvchi autentifikatsiyasi
- Izohlar tizimi (o'qish, yozish, o'chirish)
- Maqola ko'rishlar sonini kuzatish (kunlik unikal tashrif)
- To'liq matn bo'yicha qidiruv
- SEO: sitemap va robots.txt
- Parolni elektron pochta orqali tiklash
- Django Admin paneli

---

## Ishlatilgan texnologiyalar

| Texnologiya | Versiya | Tavsif |
|-------------|---------|--------|
| **Python** | 3.x | Dasturlash tili |
| **Django** | 5.1.8 | Asosiy veb-framework |
| **Django REST Framework** | ≥ 3.15 | REST API yaratish |
| **djangorestframework-simplejwt** | ≥ 5.3 | JWT autentifikatsiyasi |
| **dj-rest-auth** | — | Ro'yxatdan o'tish, tizimga kirish, parolni tiklash |
| **PostgreSQL** | — | Ma'lumotlar bazasi |
| **psycopg[binary]** | ≥ 3.1 | PostgreSQL drayveri (Python) |
| **django-cors-headers** | — | CORS (cross-origin) so'rovlarini boshqarish |
| **django-filter** | ≥ 24.0 | API so'rovlarini filtrlash |
| **martor** | — | Markdown muharrir (admin panel uchun) |
| **Pillow** | — | Rasm ishlov berish kutubxonasi |
| **python-dotenv** | ≥ 1.0 | Muhit o'zgaruvchilarini boshqarish |
| **gunicorn** | ≥ 21.2 | Production WSGI serveri |

**Deploy platforma:** Heroku (Procfile asosida — qarang: [Deploy qilish](#deploy-qilish))

---

## Loyiha tuzilmasi

```
Qaydnoma-Backend-Django/
├── config/                     # Django loyiha konfiguratsiyasi
│   ├── settings.py             # Asosiy sozlamalar
│   ├── urls.py                 # Bosh URL router
│   ├── wsgi.py                 # WSGI kirish nuqtasi
│   └── asgi.py                 # ASGI kirish nuqtasi
│
├── posts/                      # Asosiy Django ilovasi
│   ├── migrations/             # Ma'lumotlar bazasi migratsiyalari
│   ├── admin.py                # Admin panel sozlamalari
│   ├── auth_views.py           # Autentifikatsiya viewlari
│   ├── models.py               # Ma'lumotlar modellari
│   ├── permissions.py          # Maxsus ruxsat sinflari
│   ├── serializers.py          # DRF serializerlari
│   ├── sitemaps.py             # SEO sitemap konfiguratsiyasi
│   ├── urls.py                 # Ilova URL yo'nalishlari
│   └── views.py                # API viewlari
│
├── templates/
│   ├── robots.txt              # SEO robots fayli
│   └── registration/
│       └── password_reset_email.html  # Parol tiklash email shabloni
│
├── manage.py                   # Django boshqaruv skripti
├── requirements.txt            # Python kutubxonalari
├── Procfile                    # Heroku deploy konfiguratsiyasi
└── .env.example                # Muhit o'zgaruvchilari namunasi
```

---

## Ma'lumotlar bazasi modellari

### Category (Kategoriya)

| Maydon | Tur | Tavsif |
|--------|-----|--------|
| `id` | BigAutoField | Birlamchi kalit |
| `name` | CharField (120) | Kategoriya nomi (unikal) |
| `slug` | SlugField | Nomdan avtomatik yaratiladi (unikal) |

### Post (Maqola)

| Maydon | Tur | Tavsif |
|--------|-----|--------|
| `id` | BigAutoField | Birlamchi kalit |
| `category` | ForeignKey → Category | Kategoriyaga bog'liq (PROTECT) |
| `title` | CharField (255) | Sarlavha |
| `slug` | SlugField | Sarlavhadan avtomatik yaratiladi |
| `snippet` | CharField (300) | Qisqa ko'rinish matni |
| `description` | MartorField | Markdown formatdagi to'liq matn |
| `image` | BinaryField (`null=True, blank=True`) | Rasm ikkilik formatda (ixtiyoriy) |
| `image_mime` | CharField (50) | Rasm MIME turi |
| `views` | PositiveIntegerField | Ko'rishlar soni |
| `created_at` | DateTimeField | Yaratilgan vaqt (avtomatik) |

### Comment (Izoh)

| Maydon | Tur | Tavsif |
|--------|-----|--------|
| `id` | BigAutoField | Birlamchi kalit |
| `post` | ForeignKey → Post | Maqolaga bog'liq (CASCADE) |
| `user` | ForeignKey → User | Foydalanuvchiga bog'liq (CASCADE) |
| `content` | TextField (1000) | Izoh matni |
| `created_at` | DateTimeField | Yaratilgan vaqt (avtomatik) |

### PostView (Maqola ko'rishlari)

| Maydon | Tur | Tavsif |
|--------|-----|--------|
| `id` | BigAutoField | Birlamchi kalit |
| `post` | ForeignKey → Post | Maqolaga bog'liq (CASCADE) |
| `day` | DateField | Ko'rilgan kun (avtomatik) |
| `visitor_key` | CharField (64) | SHA256(IP + UserAgent) |
| `created_at` | DateTimeField | Yaratilgan vaqt (avtomatik) |

> Cheklov: `(post, day, visitor_key)` — bir tashrif etuvchi kuniga bir marta hisoblanadi.

---

## API Endpointlari

### Autentifikatsiya endpointlari

| Endpoint | Metod | Tavsif | Auth |
|----------|-------|--------|------|
| `/api/auth/register/` | POST | Ro'yxatdan o'tish | Yo'q |
| `/api/auth/token/` | POST | Tizimga kirish (JWT tokenlar olish) | Yo'q |
| `/api/auth/token/refresh/` | POST | Access tokenni yangilash | Cookie |
| `/api/auth/token/verify/` | POST | Tokenni tekshirish | JWT |
| `/api/auth/password/reset/` | POST | Parolni tiklash so'rovi | Yo'q |
| `/api/auth/password/reset/confirm/` | POST | Parolni tiklashni tasdiqlash | Yo'q |
| `/api/auth/profile/` | GET | Joriy foydalanuvchi profili | JWT |
| `/api/auth/logout/` | POST | Chiqish (tokenni bloklash) | JWT |

### Kontent endpointlari

| Endpoint | Metod | Tavsif | Auth |
|----------|-------|--------|------|
| `/api/posts/` | GET | Maqolalar ro'yxati (filtr va qidiruv bilan) | Yo'q |
| `/api/posts/` | POST | Yangi maqola yaratish | Admin/Staff |
| `/api/posts/<slug>/` | GET | Maqolani slug bo'yicha olish | Yo'q |
| `/api/posts/<int:pk>/image/` | GET | Maqola rasmini olish (binary) | Yo'q |
| `/api/categories/` | GET | Kategoriyalar ro'yxati | Yo'q |
| `/api/categories/` | POST | Yangi kategoriya yaratish | Admin/Staff |
| `/api/comments/` | GET | Izohlar ro'yxati (post bo'yicha filtr) | Yo'q |
| `/api/comments/` | POST | Yangi izoh qo'shish | JWT |
| `/api/comments/<int:pk>/` | DELETE | Izohni o'chirish | JWT + Egasi |

### Maxsus endpointlar

| Endpoint | Tavsif |
|----------|--------|
| `/admin/` | Django admin paneli |
| `/martor/` | Markdown muharrir (rasm yuklash) |
| `/sitemap.xml` | SEO sitemap |
| `/robots.txt` | SEO robots fayli |

### So'rov parametrlari (query params)

**Maqolalar filtrlash (`/api/posts/`):**

| Parametr | Tavsif |
|----------|--------|
| `?category=<slug>` | Kategoriya bo'yicha filtrlash |
| `?q=<qidiruv>` | To'liq matn qidiruvi (sarlavha, snippet, tavsif) |

**Izohlar filtrlash (`/api/comments/`):**

| Parametr | Tavsif |
|----------|--------|
| `?post=<id>` | Maqola ID si bo'yicha filtrlash |

> **Paginatsiya:** Har bir sahifada 12 ta element ko'rsatiladi.

---

## Autentifikatsiya

Tizim **JWT (JSON Web Token)** asosida ishlaydi.

| Parametr | Qiymat |
|----------|--------|
| **Access token muddati** | 10 daqiqa (`config/settings.py` da o'zgartiriladi) |
| **Refresh token muddati** | 7 kun (`config/settings.py` da o'zgartiriladi) |
| **Algoritm** | HS512 |
| **Token rotatsiyasi** | Yoqilgan |
| **Blacklist** | Yoqilgan (chiqishda token bloklanadi) |

**Tokenlarni saqlash usuli:**
- **Access token** — javob tanasida qaytariladi (client tomonida saqlanadi)
- **Refresh token** — `HttpOnly` cookie sifatida saqlanadi (JavaScript orqali o'qib bo'lmaydi)

---

## O'rnatish va ishga tushirish

### Talablar

- Python 3.10+
- PostgreSQL
- pip

### Qadamlar

```bash
# 1. Repozitoriyani klonlash
git clone https://github.com/Zarifwebme/Qaydnoma-Backend-Django.git
cd Qaydnoma-Backend-Django

# 2. Virtual muhit yaratish va faollashtirish
python -m venv venv
source venv/bin/activate        # Linux / macOS
# yoki
venv\Scripts\activate           # Windows

# 3. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 4. Muhit o'zgaruvchilarini sozlash
cp .env.example .env
# .env faylini o'z ma'lumotlaringiz bilan to'ldiring

# 5. Ma'lumotlar bazasini migratsiya qilish
python manage.py migrate

# 6. Superuser yaratish
python manage.py createsuperuser

# 7. Serverni ishga tushirish
python manage.py runserver
```

Ilova `http://127.0.0.1:8000/` manzilida ishlaydi.

---

## Muhit o'zgaruvchilari

`.env.example` faylini nusxa olib `.env` nomini bering va quyidagi o'zgaruvchilarni to'ldiring:

```env
# Django
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=1                        # 0 — production, 1 — development

# PostgreSQL
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail SMTP)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

---

## Deploy qilish

Loyiha **Heroku** ga deploy qilish uchun sozlangan:

```bash
# Heroku CLI orqali
heroku create
heroku config:set DJANGO_SECRET_KEY=...
heroku config:set DJANGO_DEBUG=0
# Boshqa muhit o'zgaruvchilarini ham kiriting

git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

Production serverda **Gunicorn** ishlatiladi:

```
web: gunicorn config.wsgi
```

---

## Litsenziya

Ushbu loyiha ochiq manbali bo'lib, [MIT litsenziyasi](LICENSE) ostida tarqatiladi.
