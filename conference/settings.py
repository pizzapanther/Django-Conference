from django.conf import settings

SPONSOR_NOTIFY = getattr(settings, 'CONF_SPONSOR_NOTIFY', ())
SPEAKER_NOTIFY = getattr(settings, 'CONF_SPEAKER_NOTIFY', ())

SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost')
SITE_PROTOCOL = getattr(settings, 'SITE_PROTOCOL', 'http')
