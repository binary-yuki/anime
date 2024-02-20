import json
import subprocess
from contextlib import asynccontextmanager
from celery.result import AsyncResult
from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, Response

from worker import *
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        time.sleep(30)
        from prisma import Prisma
        Prisma()
        yield
    except Exception as e:
        time.sleep(30)
        os.system("prisma generate")
        os.system("prisma db push")


@app.post("/tasks", status_code=201)
def run_task(payload=Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result


@app.get("/prisma_status")
async def prisma_status(request: Request):
    try:
        db = Prisma()
        await db.connect()
        f = await db.user.find_many()
        await db.disconnect()
        return JSONResponse({"status": "connected", "data": f})
    except ConnectionError as e:
        return JSONResponse({"error": str(e)})
    except Exception as e:
        cmd1 = subprocess.run(["prisma", "generate"]).stdout
        cmd2 = subprocess.run(["prisma", "db", "push"]).stdout
        return JSONResponse({"error": str(e), "cmd1_output": cmd1, "cmd2_output": cmd2})


@app.get("/create")
async def create(request: Request):
    data = request.query_params.get("id")
    ls = [data]
    task = create_query_task.delay(ls)
    return RedirectResponse(url=f"/create/{task.id}", status_code=302)


@app.post("/create/{qid}")
async def create(request: Request, qid: str):
    # 根据 id 查询任务状态
    task_status = AsyncResult(qid).status
    if task_status == "SUCCESS":
        return RedirectResponse(url=f"/result/{qid}", status_code=302)
    elif task_status == "PENDING":
        return RedirectResponse(url=f"/tasks/{qid}", status_code=302)
    else:
        # 失败 返回/重新创建
        referer = request.headers.get("referer")
        return RedirectResponse(url=referer, status_code=302)


@app.get("/create/{qid}")
async def create(request: Request, qid: str):
    templates = Jinja2Templates("templates")
    return templates.TemplateResponse("loading.html", {"request": request, "qid": qid})


@app.get("/result/{qid}")
async def result(request: Request, qid: str):
    task_status = AsyncResult(qid).status
    if task_status == "SUCCESS":
        task_result = AsyncResult(qid).result
        return JSONResponse(
            {"status": "success", "task_id": qid, "task_status": task_status, "task_result": task_result},
            status_code=200)
    elif task_status == "PENDING":
        return RedirectResponse(url=f"/tasks/{qid}", status_code=302)
    else:
        return JSONResponse({"status": "failed", "task_id": qid, "task_status": task_status}, status_code=400)
