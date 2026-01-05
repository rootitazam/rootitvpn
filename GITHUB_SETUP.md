# راهنمای آپلود پروژه به GitHub

## مرحله 1: نصب Git (اگر نصب نیست)

### Windows:
1. دانلود Git از: https://git-scm.com/download/win
2. نصب با تنظیمات پیش‌فرض
3. باز کردن PowerShell یا CMD جدید

### بررسی نصب:
```bash
git --version
```

## مرحله 2: تنظیم Git (اولین بار)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## مرحله 3: ایجاد Repository در GitHub

1. وارد GitHub شوید: https://github.com
2. کلیک روی **New Repository** (یا + → New repository)
3. نام repository را وارد کنید (مثلاً: `rootitvpn`)
4. **Public** یا **Private** را انتخاب کنید
5. **توجه**: گزینه "Initialize with README" را انتخاب نکنید
6. روی **Create repository** کلیک کنید
7. آدرس repository را کپی کنید (مثلاً: `https://github.com/username/rootitvpn.git`)

## مرحله 4: راه‌اندازی Git در پروژه

در PowerShell یا CMD، در مسیر پروژه (`C:\Users\Peymani\Desktop\rootitvpn`) اجرا کنید:

```bash
# Initialize Git repository
git init

# اضافه کردن تمام فایل‌ها
git add .

# ایجاد اولین commit
git commit -m "Initial commit: RootitVPN Panel - Complete VPN Management System"

# اضافه کردن remote repository (آدرس را از GitHub کپی کنید)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push به GitHub
git branch -M main
git push -u origin main
```

## مرحله 5: دستورات بعدی (برای به‌روزرسانی)

هر بار که تغییری می‌دهید:

```bash
git add .
git commit -m "توضیح تغییرات"
git push
```

## نکات مهم:

1. **فایل `.env`**: این فایل در `.gitignore` است و به GitHub ارسال نمی‌شود (امنیت)
2. **Database**: فایل‌های `.db` هم ignore شده‌اند
3. **GeoIP/Geosite**: فایل‌های geoip.dat و geosite.dat باید جداگانه دانلود شوند

## اگر خطا گرفتید:

### خطای Authentication:
```bash
# استفاده از Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
```

### خطای "repository not found":
- مطمئن شوید آدرس repository درست است
- مطمئن شوید به repository دسترسی دارید

### خطای "nothing to commit":
- فایل‌ها را بررسی کنید: `git status`
- ممکن است همه فایل‌ها ignore شده باشند

## دستورات مفید:

```bash
# بررسی وضعیت
git status

# مشاهده تغییرات
git diff

# مشاهده تاریخچه
git log

# حذف remote (اگر اشتباه اضافه کردید)
git remote remove origin
```

