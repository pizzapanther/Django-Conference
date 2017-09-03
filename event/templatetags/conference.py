from django import template
from django.conf import settings

import os

register = template.Library()


@register.filter
def json_attr(path):
  root, ext = os.path.splitext(path)
  root = root.split('/')[-1]

  return root

@register.filter
def dist(path, d):
  return os.path.join(settings.FRONTEND, d, path)
  