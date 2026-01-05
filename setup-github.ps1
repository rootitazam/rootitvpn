# اسکریپت راه‌اندازی Git و آپلود به GitHub
# RootitVPN Project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RootitVPN - GitHub Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی نصب Git
Write-Host "بررسی نصب Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✓ Git نصب است: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git نصب نیست!" -ForegroundColor Red
    Write-Host ""
    Write-Host "لطفاً Git را از آدرس زیر دانلود و نصب کنید:" -ForegroundColor Yellow
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "بعد از نصب، این اسکریپت را دوباره اجرا کنید." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# بررسی اینکه آیا repository وجود دارد
if (Test-Path .git) {
    Write-Host "✓ Git repository از قبل وجود دارد" -ForegroundColor Green
} else {
    Write-Host "ایجاد Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Repository ایجاد شد" -ForegroundColor Green
}

Write-Host ""

# اضافه کردن فایل‌ها
Write-Host "اضافه کردن فایل‌ها به Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ فایل‌ها اضافه شدند" -ForegroundColor Green

Write-Host ""

# بررسی تغییرات
$status = git status --short
if ($status) {
    Write-Host "فایل‌های آماده commit:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    
    # ایجاد commit
    Write-Host "ایجاد commit..." -ForegroundColor Yellow
    git commit -m "Initial commit: RootitVPN Panel - Complete VPN Management System"
    Write-Host "✓ Commit ایجاد شد" -ForegroundColor Green
} else {
    Write-Host "هیچ تغییری برای commit وجود ندارد" -ForegroundColor Yellow
}

Write-Host ""

# درخواست آدرس GitHub repository
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "تنظیم Remote Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "لطفاً آدرس GitHub repository خود را وارد کنید:" -ForegroundColor Yellow
Write-Host "مثال: https://github.com/username/rootitvpn.git" -ForegroundColor Gray
Write-Host "یا: git@github.com:username/rootitvpn.git" -ForegroundColor Gray
Write-Host ""

$repoUrl = Read-Host "آدرس Repository"

if ($repoUrl) {
    Write-Host ""
    Write-Host "اضافه کردن remote repository..." -ForegroundColor Yellow
    
    # حذف remote قبلی اگر وجود دارد
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote) {
        Write-Host "حذف remote قبلی..." -ForegroundColor Yellow
        git remote remove origin
    }
    
    git remote add origin $repoUrl
    Write-Host "✓ Remote repository اضافه شد" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "تغییر branch به main..." -ForegroundColor Yellow
    git branch -M main
    Write-Host "✓ Branch به main تغییر کرد" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "آماده برای Push!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "برای push کردن به GitHub، دستور زیر را اجرا کنید:" -ForegroundColor Yellow
    Write-Host "git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "یا اگر از Personal Access Token استفاده می‌کنید:" -ForegroundColor Yellow
    Write-Host "git push https://YOUR_TOKEN@github.com/USERNAME/REPO.git main" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "آدرس repository وارد نشد. می‌توانید بعداً با دستور زیر اضافه کنید:" -ForegroundColor Yellow
    Write-Host "git remote add origin YOUR_REPO_URL" -ForegroundColor Cyan
    Write-Host "git push -u origin main" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "برای اطلاعات بیشتر، فایل GITHUB_SETUP.md را مطالعه کنید." -ForegroundColor Gray

