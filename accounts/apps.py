from django.apps import AppConfig


def _patch_django_seed_timezone():
    """django-seed 0.3.1 uses make_aware(..., is_dst=); removed in Django 5+."""
    try:
        import django_seed.guessers as guessers_module
    except ImportError:
        return
    from django.conf import settings
    from django.utils import timezone

    def _timezone_format(value):
        if getattr(settings, 'USE_TZ', False):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    guessers_module._timezone_format = _timezone_format


class AccountsConfig(AppConfig):
    name = 'accounts'
    def ready(self):
        import accounts.signals
        _patch_django_seed_timezone()