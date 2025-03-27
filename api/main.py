# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from dotenv import load_dotenv
import os

import uvicorn

with open("README.md", "r") as file:
    description = file.read()

load_dotenv()

port = os.getenv("PORT", "5021")

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


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(port))