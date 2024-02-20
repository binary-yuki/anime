import os
import time


time.sleep(30)
os.system("prisma generate")
os.system("prisma db push")
os.system("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
