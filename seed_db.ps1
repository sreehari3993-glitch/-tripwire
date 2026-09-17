# Tripwire — Seed Database
# Run this ONCE before starting the backend

$PY = "C:\Users\sreeh\AppData\Local\Programs\Python\Python312\python.exe"

Set-Location backend
& $PY seed_data.py
Write-Host ""
Write-Host "✅ Database seeded. You can now start the backend." -ForegroundColor Green
Write-Host "   Login: FAC001 / tripwire123" -ForegroundColor Cyan
