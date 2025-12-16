import multiprocessing
import os

bind = "0.0.0.0:8000"

worker_class = "hypercorn.workers.HypercornWorker"

workers = 1  

loglevel = "info"
accesslog = "-"
errorlog = "-"