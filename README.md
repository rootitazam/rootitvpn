# RootitVPN | روتیت - VPN Management Panel

پنل مدیریت حرفه‌ای VPN برای Xray-core با قابلیت‌های پیشرفته برای دور زدن فیلترینگ شدید و سرعت بالا.

## ⚡ نصب سریع (یک دستور)

```bash
curl -fsSL https://raw.githubusercontent.com/rootitazam/rootitvpn/main/install.sh | bash
```

یا:

```bash
wget -qO- https://raw.githubusercontent.com/rootitazam/rootitvpn/main/install.sh | bash
```

**این اسکریپت به صورت خودکار:**
- ✅ Docker و Docker Compose را نصب می‌کند
- ✅ پروژه را از GitHub کلون می‌کند
- ✅ فایل `.env` را با تنظیمات پیش‌فرض ایجاد می‌کند
- ✅ GeoIP/Geosite را دانلود می‌کند
- ✅ سرویس‌ها را راه‌اندازی می‌کند

## 📋 نصب دستی

### پیش‌نیازها

- Ubuntu 22.04 LTS (یا Debian 11+)
- دسترسی root

### مراحل نصب

```bash
# 1. دانلود اسکریپت نصب
wget https://raw.githubusercontent.com/rootitazam/rootitvpn/main/install.sh

# 2. اجرای اسکریپت
chmod +x install.sh
sudo ./install.sh
```

یا اگر از قبل پروژه را کلون کرده‌اید:

```bash
cd /opt/rootitvpn
chmod +x install.sh
sudo ./install.sh
```

## 🚀 ویژگی‌ها

- ✅ مدیریت کاربران (CRUD) با ردیابی مصرف داده و تاریخ انقضا
- ✅ مانیتورینگ پیشرفته: کاربران آنلاین، Device Fingerprints، Domain Sniffing (SNI logging)
- ✅ مدیریت لاگ: چرخش و حذف خودکار 24 ساعته
- ✅ پروتکل VLESS + Reality + XTLS-RPX-Vision
- ✅ Fragment برای دور زدن DPI
- ✅ TCP Fast Open برای سرعت بالا
- ✅ چرخش خودکار تنظیمات Reality
- ✅ تولید لینک اشتراک‌گذاری برای v2rayNG، Shadowrocket، Nekoray
- ✅ Routing Rules: IP های ایران و دامنه‌های .ir به صورت DIRECT
- ✅ تنظیم Server IP از پنل گرافیکی

## 📁 ساختار پروژه

```
rootitvpn/
├── backend/          # FastAPI Backend
├── frontend/         # React Frontend
├── xray/            # Xray Configuration
├── install.sh       # اسکریپت نصب خودکار
└── docker-compose.yml
```

## 🔧 تنظیمات اولیه

بعد از نصب:

1. **وارد پنل شوید:**
   - آدرس: `http://YOUR_SERVER_IP:3000`
   - Username: `admin`
   - Password: (در فایل `.env` یا خروجی نصب نمایش داده می‌شود)

2. **تغییر رمز عبور:**
   - بعد از اولین ورود، رمز عبور admin را تغییر دهید

3. **تنظیم Server IP:**
   - به بخش "تنظیمات" بروید
   - Server IP را بررسی/تنظیم کنید

4. **تنظیمات Reality:**
   - Reality Dest و Server Names را بررسی کنید

5. **ایجاد کاربر:**
   - به بخش "مدیریت کاربران" بروید
   - کاربر جدید ایجاد کنید
   - لینک اشتراک‌گذاری را دریافت کنید

## 🔥 باز کردن Firewall

```bash
# نصب UFW
sudo apt install -y ufw

# باز کردن پورت‌ها
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 443/tcp   # Xray VPN
sudo ufw allow 8080/tcp  # Xray gRPC

# فعال‌سازی
sudo ufw enable
```

## 📝 دستورات مفید

```bash
# مشاهده لاگ‌ها
docker-compose logs -f

# راه‌اندازی مجدد
docker-compose restart

# توقف سرویس‌ها
docker-compose down

# راه‌اندازی مجدد
docker-compose up -d

# بررسی وضعیت
docker-compose ps

# مشاهده لاگ یک سرویس خاص
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f xray
```

## 🔄 به‌روزرسانی

```bash
cd /opt/rootitvpn
git pull
docker-compose down
docker-compose up -d --build
```

## 🛠️ تکنولوژی‌ها

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Tailwind CSS, Vite
- **Core**: Xray-core (Latest)
- **Communication**: gRPC
- **Containerization**: Docker & Docker Compose

## 🔒 امنیت

- Session-based authentication
- Password hashing با bcrypt
- CSRF protection
- Rate limiting
- Environment variables برای اطلاعات حساس

## 📄 مجوز

این پروژه برای استفاده شخصی و تجاری آزاد است.

## 🆘 پشتیبانی

برای مشکلات و سوالات:
- Issues: https://github.com/rootitazam/rootitvpn/issues
- Repository: https://github.com/rootitazam/rootitvpn

---

**ساخته شده با ❤️ برای دور زدن فیلترینگ**
