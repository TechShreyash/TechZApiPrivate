import multiprocessing
import os

name = "Gunicorn config for FastAPI"

accesslog = "/home/user/fastapi/gunicorn-access.log"
errorlog = "/home/user/fastapi/gunicorn-error.log"

bind = "0.0.0.0:8000"

worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
print(workers)
