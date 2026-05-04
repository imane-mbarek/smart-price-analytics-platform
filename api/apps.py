from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        Appelé une seule fois au démarrage de Django.
        Lance le scraping périodique en arrière-plan.
        """
        import os
        # Éviter le double démarrage avec le reloader Django en développement
        if os.environ.get('RUN_MAIN') != 'true':
            return
        from . import scheduler
        scheduler.demarrer()
