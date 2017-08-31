from django import http
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.template.response import TemplateResponse
from django.templatetags.static import static

from pytx.files import JS, CSS, FONTS, IMAGES, MD, tpl_files
from pytx.release import RELEASE, DEV

def site_context(context):
  context['site'] = {'name': 'PyTexas'}

  tpls = tpl_files()

  context['debug'] = DEV
  context['release'] = RELEASE
  context['conf'] = settings.CURRENT_CONF
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
def favicon(request):
  return http.HttpResponseRedirect(static('favicon.ico'))


@cache_page(60 * 5, key_prefix=RELEASE)
def frontend(request):
  if request.path == '/':
    return http.HttpResponseRedirect("/{}/".format(settings.CURRENT_CONF))

  context = {}
  return TemplateResponse(request, 'frontend.html', site_context(context))


@cache_page(60 * 5, key_prefix=RELEASE)
def sw(request):
  context = {}
  return TemplateResponse(
      request,
      'service-worker.js',
      site_context(context),
      content_type="application/javascript")
