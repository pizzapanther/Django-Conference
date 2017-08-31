from django import template

import os

register = template.Library()

@register.filter
def json_attr (path):
  root, ext = os.path.splitext(path)
  root = root.split('/')[-1]
  
  return root
  