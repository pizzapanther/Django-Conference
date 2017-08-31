from django import http
from django.views.decorators.cache import cache_page
from django.template.response import TemplateResponse
from django.templatetags.static import static

from pytx.files import JS, CSS, FONTS, IMAGES, MD, tpl_files
from pytx.release import RELEASE, DEV

def site_context (context):
  context['site'] = {
    'name': 'PyTexas'
  }
  
  tpls = tpl_files()
  
  context['debug'] = DEV
  context['release'] = RELEASE
  context['files'] = {
    'js': JS,
    'css': CSS,
    'fonts': FONTS,
    'images': IMAGES,
    'md': MD,
    'templates': tpls,
  }
  
  return context
  
@cache_page(60 * 5, key_prefix=RELEASE)
def favicon (request):
  return http.HttpResponseRedirect(static('favicon.ico'))
  
@cache_page(60 * 5, key_prefix=RELEASE)
def frontend (request):
  context = {}
  return TemplateResponse(request, 'frontend.html', site_context(context))
  