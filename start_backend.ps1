# Tripwire — Start Backend
# Run this from the hackathon root directory

$PY = "C:\Users\sreeh\AppData\Local\Programs\Python\Python312\python.exe"

Set-Location backend
& $PY -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
