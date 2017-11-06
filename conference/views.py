import hashlib

from django import http
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse
from django.templatetags.static import static

from pytx.files import JS, JS_HEAD, CSS, FONTS, IMAGES, MD, tpl_files
from pytx.release import RELEASE, DEV, DATA, release_key
from pytx.schema import schema

class CachePage:
  def __init__ (self, timeout=60 * 5, key_prefix=release_key):
    self.timeout = timeout
    self.key_prefix = key_prefix
    self.target = None
    
  def __call__ (self, target):
    self.target = target
    return self.run
    
  def run (self, *args, **kw):
    cache_key = self.key_prefix() + args[0].get_full_path()
    cache_key = hashlib.sha1(cache_key.encode('utf-8')).hexdigest()
    
    cached_response = cache.get(cache_key)
    if cached_response:
      cached_response['PageCached'] = 'True'
      return cached_response
      
    response = self.target(*args, **kw)
    
    print('Caching:', args[0].get_full_path())
    if hasattr(response, 'render') and callable(response.render):
      response.add_post_render_callback(
        lambda r: cache.set(cache_key, r, self.timeout)
      )
      
    else:
      cache.set(cache_key, response, self.timeout)
      
    return response
    
def site_context(context):
  context['site'] = {'name': 'PyTexas'}

  tpls = tpl_files()

  context['debug'] = DEV
  context['release'] = release_key()
  context['conf'] = settings.CURRENT_CONF
  context['base_url'] = settings.BASE_URL
  context['skip_sw'] = getattr(settings, 'SKIP_SW', False)
  context['files'] = {
      'js': JS,
      'js_head': JS_HEAD,
      'css': CSS,
      'fonts': FONTS,
      'images': IMAGES,
      'md': MD,
      'templates': tpls,
  }

  return context


@CachePage()
def favicon(request):
  return http.HttpResponseRedirect(static('favicon.ico'))


@CachePage()
@never_cache
def frontend(request):
  if request.path == '/':
    return http.HttpResponseRedirect("/{}/".format(settings.CURRENT_CONF))

  context = {}
  return TemplateResponse(request, 'frontend.html', site_context(context))


@CachePage()
@never_cache
def sw(request):
  context = {}
  return TemplateResponse(
      request,
      'service-worker.js',
      site_context(context),
      content_type="application/javascript")


@CachePage()
def release(request):
  return http.JsonResponse({'release': release_key()})


@CachePage()
def manifest(request):
  return TemplateResponse(
      request,
      'manifest.json',
      site_context({}),
      content_type="application/x-web-app-manifest+json")


@CachePage()
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
                    logo
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
  allSessions(status: "accepted") {
    edges{
      node{
        id
        name
        description
        duration
        start
        startStr
        endStr
        status
        allRooms
        room {
          id
          name
        }

        user{
          id
          name
          biography
          image
          website
          
          socialHandles{
            edges{
              node{
                id
                site
                username
              }
            }
          }
        }
      }
    }
  }
  allKeynotes(stype: "keynote") {
    edges{
      node{
        id
        name
        description

        user{
          id
          name
          title
          biography
          avatar
        }
      }
    }
  }
}
"""


@CachePage()
def conference_data(request, slug):
  query = QUERY.replace('{slug}', slug)
  result = schema.execute(query)
  if result.invalid:
      return http.JsonResponse({
        'errors': [str(error) for error in result.errors]
      })
  return http.JsonResponse(result.data)
