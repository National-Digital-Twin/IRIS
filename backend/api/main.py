# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


import asyncpg.exceptions
import sqlalchemy.exc
import uvicorn
from config import get_settings
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import router

config_settings = get_settings()

with open("README.md", "r") as file:
    description = file.read()

app = FastAPI(
    title="NDT Assessment Write-Back API",
    description=description,
    docs_url="/api-docs",
    openapi_url="/api-docs/openapi.json",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(sqlalchemy.exc.DBAPIError)
async def query_timeout_handler(request: Request, exc: sqlalchemy.exc.DBAPIError):
    sqlstate = getattr(exc.orig, "sqlstate", None)
    if sqlstate == asyncpg.exceptions.QueryCanceledError.sqlstate:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "detail": "The request took too long to complete.",
                "error": "QueryCanceledError",
            },
        )

    raise exc


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(config_settings.PORT))
