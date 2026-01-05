# RootitVPN | روتیت - VPN Management Panel

پنل مدیریت حرفه‌ای VPN برای Xray-core با قابلیت‌های پیشرفته برای دور زدن فیلترینگ شدید و سرعت بالا.

> **نکته**: برای راهنمای کامل آپلود به GitHub، فایل `GITHUB_SETUP.md` را مطالعه کنید.

## ویژگی‌ها

- ✅ مدیریت کاربران (CRUD) با ردیابی مصرف داده و تاریخ انقضا
- ✅ مانیتورینگ پیشرفته: کاربران آنلاین، Device Fingerprints، Domain Sniffing (SNI logging)
- ✅ مدیریت لاگ: چرخش و حذف خودکار 24 ساعته
- ✅ پروتکل VLESS + Reality + XTLS-RPX-Vision
- ✅ Fragment برای دور زدن DPI
- ✅ TCP Fast Open برای سرعت بالا
- ✅ چرخش خودکار تنظیمات Reality
- ✅ تولید لینک اشتراک‌گذاری برای v2rayNG، Shadowrocket، Nekoray
- ✅ Routing Rules: IP های ایران و دامنه‌های .ir به صورت DIRECT

## ساختار پروژه

```
rootitvpn/
├── backend/          # FastAPI Backend
├── frontend/         # React Frontend
├── xray/            # Xray Configuration
└── docker-compose.yml
```

## نصب و راه‌اندازی

### پیش‌نیازها

- Docker & Docker Compose
- Ubuntu 22.04 LTS (برای سرور)

### 1. کلون کردن پروژه

```bash
git clone <repository-url>
cd rootitvpn
```

### 2. تنظیم Environment Variables

```bash
cp .env.example .env
# ویرایش .env و تنظیم مقادیر مورد نیاز
```

### 3. دانلود فایل‌های GeoIP/Geosite (اختیاری)

```bash
chmod +x xray/download-geo.sh
./xray/download-geo.sh
```

### 4. نصب Xray-core روی سرور (اگر از Docker استفاده نمی‌کنید)

```bash
chmod +x xray/install.sh
sudo ./xray/install.sh
```

### 5. راه‌اندازی با Docker Compose

```bash
docker-compose up -d
```

### 6. دسترسی به پنل

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## تنظیمات اولیه

1. وارد پنل شوید با اطلاعات admin از `.env`
2. تنظیمات Reality را پیکربندی کنید
3. کاربران را ایجاد کنید
4. لینک‌های اشتراک‌گذاری را تولید کنید

## تکنولوژی‌ها

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Tailwind CSS, Vite
- **Core**: Xray-core (Latest)
- **Communication**: gRPC

## امنیت

- Session-based authentication
- Password hashing با bcrypt
- CSRF protection
- Rate limiting

## مجوز

این پروژه برای استفاده شخصی و تجاری آزاد است.

# rootitvpn
