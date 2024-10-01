import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from backend.models import ScheduledJob

# Dynamically construct the database URL based on the environment
if os.getenv("ENV_DATABASE") == "PROD":
    db_name = os.getenv("PROD_DB_NAME")
    db_user = os.getenv("PROD_DB_USER")
    db_password = os.getenv("PROD_DB_PASSWORD")
    db_host = os.getenv("PROD_DB_HOST")
    db_port = os.getenv("PROD_DB_PORT")
else:
    db_name = os.getenv("LOCAL_DB_NAME")
    db_user = os.getenv("LOCAL_DB_USER")
    db_password = os.getenv("LOCAL_DB_PASSWORD")
    db_host = os.getenv("LOCAL_DB_HOST")
    db_port = os.getenv("LOCAL_DB_PORT")

# Create the database URL
database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Configure job stores with the constructed URL
jobstores = {"default": SQLAlchemyJobStore(url=database_url)}

# Initialize the scheduler
scheduler = BackgroundScheduler(jobstores=jobstores)


def remove_job_from_db(event):
    """Remove job from the database when it is successfully executed."""
    job_id = event.job_id

    try:
        # Fetch the ScheduledJob object by job_id
        job = ScheduledJob.objects.get(job_id=job_id)
        job.delete()  # Remove the job from the database
        print(f"Job {job_id} successfully executed and removed from DB.")
    except ScheduledJob.DoesNotExist:
        print(f"Job {job_id} not found in the database.")


def job_listener(event):
    """Listen for job events and remove the job if it has been executed successfully."""
    if event.exception:
        print(f"Job {event.job_id} failed with exception: {event.exception}")
    else:
        # If the job ran successfully, remove it from the database
        remove_job_from_db(event)


def start_scheduler():
    # Start the scheduler
    scheduler.start()

    # Add the listener to detect when jobs complete
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
