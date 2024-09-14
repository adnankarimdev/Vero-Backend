from django.apps import AppConfig
from .scheduler import start_scheduler


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

class MyAppConfig(AppConfig):
    name = 'backend'

    def ready(self):
        # Start the scheduler when the application is ready
        start_scheduler()