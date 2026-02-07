"""Auto-register all app models in Django Admin."""
from django.contrib import admin
from django.apps import apps

# Auto-register all models from our custom apps
APP_LABELS = [
    'inventory', 'fault', 'configuration', 'performance',
    'security', 'ptp', 'war_mode', 'ntg',
]

for app_label in APP_LABELS:
    try:
        app_config = apps.get_app_config(app_label)
        for model in app_config.get_models():
            if not admin.site.is_registered(model):
                admin.site.register(model)
    except LookupError:
        pass
