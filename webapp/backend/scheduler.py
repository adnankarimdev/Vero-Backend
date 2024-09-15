# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize the scheduler
scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.start()
