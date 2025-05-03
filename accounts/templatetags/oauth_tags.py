from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def google_client_id():
    return settings.GOOGLE_OAUTH_CLIENT_ID
