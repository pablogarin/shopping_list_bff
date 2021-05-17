import multiprocessing
import os


PORT = os.getenv("PORT", 5000)
bind = f"0.0.0.0:{PORT}"
workers = 2 * multiprocessing.cpu_count() - 1
threads = 4 * multiprocessing.cpu_count()
timeout = 30
