from django import http
from django.conf import settings
from django.views.decorators.cache import cache_page, never_cache
from django.template.response import TemplateResponse
from django.templatetags.static import static

from pytx.files import JS, CSS, FONTS, IMAGES, MD, tpl_files
from pytx.release import RELEASE, DEV
from pytx.schema import schema

def site_context(context):
  context['site'] = {'name': 'PyTexas'}

  tpls = tpl_files()

  context['debug'] = DEV
  context['release'] = RELEASE
  context['conf'] = settings.CURRENT_CONF
  context['base_url'] = settings.BASE_URL
  context['skip_sw'] = getattr(settings, 'SKIP_SW', False)
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
@never_cache
def frontend(request):
  if request.path == '/':
    return http.HttpResponseRedirect("/{}/".format(settings.CURRENT_CONF))

  context = {}
  return TemplateResponse(request, 'frontend.html', site_context(context))


@cache_page(60 * 5, key_prefix=RELEASE)
@never_cache
def sw(request):
  context = {}
  return TemplateResponse(
      request,
      'service-worker.js',
      site_context(context),
      content_type="application/javascript")


@cache_page(60 * 5, key_prefix=RELEASE)
def release(request):
  return http.JsonResponse({'release': RELEASE})


@cache_page(60 * 5, key_prefix=RELEASE)
def manifest(request):
  return TemplateResponse(
      request,
      'manifest.json',
      site_context({}),
      content_type="application/json")


@cache_page(60 * 5, key_prefix=RELEASE)
def browserconfig(request):
  return TemplateResponse(
      request,
      'browserconfig.xml',
      site_context({}),
      content_type="application/xml")

QUERY = """
query {
  allConfs(slug: "{slug}" first: 1) {
    edges{
      node{
        id
        name
        slug
        
        sponsorshiplevelSet{
          edges{
            node{
              id
              name
              description
              
              sponsorSet(active: true){
                edges{
                  node{
                    id
                    name
                    description
                    url
                    logoUrl
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

@cache_page(60 * 5, key_prefix=RELEASE)
def conference_data(request, slug):
  query = QUERY.replace('{slug}', slug)
  result = schema.execute(query)
  return http.JsonResponse(result.data)
  