# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "social_app"

# Timeout
timeout = 120

# Keep the workers alive for fast reloads
keepalive = 5

# Maximum requests before worker restart
max_requests = 1000
max_requests_jitter = 50 
