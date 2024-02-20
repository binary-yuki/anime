from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict
from starlette.requests import Request

app = FastAPI()


class PathNotFoundException(HTTPException):
    def __init__(self, path: str):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"{path} not found"
        self.timestamp = int(str(datetime.now()))


class InvalidParamException(HTTPException):
    def __init__(self, param_lost: Any):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Invalid Param: {param_lost}"
        self.timestamp = int(str(datetime.now()))
        self.headers = {"X-Error": "Param Lost"}


@app.exception_handler(PathNotFoundException)
async def handle_path_not_found_exception(request: Request, exc: PathNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"timestamp": exc.timestamp, "message": exc.detail}
    )


@app.exception_handler(InvalidParamException)
async def handle_invalid_item_exception(request: Request, exc: InvalidParamException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"timestamp": exc.timestamp, "message": exc.detail},
        headers=exc.headers
    )
