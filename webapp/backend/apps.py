from django.apps import AppConfig
from django.apps import apps
import json  # For converting JSON string back to a list
import importlib  # For dynamic imports
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

class BackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend"

    def ready(self):
        # Delay the import of scheduler components until the app is ready
        from .scheduler import start_scheduler, scheduler, job_listener

        # Start the scheduler when the application is ready
        start_scheduler()
        print("App has begun")

        # Clear all jobs on startup
        scheduler.remove_all_jobs()

        # Ensure models are loaded before accessing them
        self.reinitialize_jobs()

        # Add listener for job execution and error handling
        scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def reinitialize_jobs(self):
        # Import scheduler again here to ensure access
        from .scheduler import scheduler  # Import the scheduler here to make it accessible

        # Get the ScheduledJob model using the apps registry
        ScheduledJob = apps.get_model('backend', 'ScheduledJob')
        scheduled_jobs = ScheduledJob.objects.all()

        # Dynamically import the views only when needed
        views = importlib.import_module('backend.views')

        for job in scheduled_jobs:
            # Convert args back from JSON string to list
            args = json.loads(job.args)  # Assuming you stored args as JSON string
            if job.job_name == 'send_text':
                scheduler.add_job(
                    views.send_text,
                    "date",
                    run_date=job.run_date,
                    args=args,
                    id=job.job_id  # Ensure unique ID to prevent duplicate jobs
                )
            elif job.job_name == 'send_scheduled_email':
                scheduler.add_job(
                    views.send_sceduled_email,
                    "date",
                    run_date=job.run_date,
                    args=args,
                    id=job.job_id
                )
            elif job.job_name == 'send_scheduled_concern_email':
                scheduler.add_job(
                    views.send_scheduled_concern_email,
                    "date",
                    run_date=job.run_date,
                    args=args,
                    id=job.job_id
                )