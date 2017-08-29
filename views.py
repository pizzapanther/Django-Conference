
from django import http

def frontend (request):
  return http.HttpResponse('Coming Soon', content_type="text/plain")