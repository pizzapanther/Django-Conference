import hashlib
import random
import datetime

from functools import update_wrapper

from django.contrib import admin
from django.db import models
from django import http
from django.contrib.admin.views.main import ChangeList, IGNORED_PARAMS

from conference.event.models import Conference, SponsorshipLevel, Sponsor, Session, Invoice, Room
from conference.utils import CSVFileGenerator

CSV_IGNORED = [p for p in IGNORED_PARAMS]
CSV_IGNORED.append('csv')
CSV_IGNORED.append('nocache')


class CSVChangeList(ChangeList):

  def get_filters_params(self, params=None):
    if not params:
      params = self.params

    lookup_params = params.copy()
    for ignored in CSV_IGNORED:
      if ignored in lookup_params:
        del lookup_params[ignored]

    return lookup_params


class CSVAdminMixin(object):

  def changelist_view(self, request, extra_context=None):
    csv = request.GET.get('csv', '')
    if csv == '1':
      list_display = self.get_list_display(request)
      list_display_links = self.get_list_display_links(request, list_display)
      list_filter = self.get_list_filter(request)

      cl = CSVChangeList(request, self.model, list_display, list_display_links,
                         list_filter, self.date_hierarchy, self.search_fields,
                         self.list_select_related, self.list_per_page,
                         self.list_max_show_all, self.list_editable, self)

      generator = CSVFileGenerator(
          queryset=cl.get_queryset(request), tags=self.csv_rows)
      return generator.getIteratorResponse()

    return super(CSVAdminMixin, self).changelist_view(
        request, extra_context=extra_context)


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug', 'start', 'end', 'active', 'registration_open',
                  'registration_closed')
  list_filter = ('active',)
  list_editable = ('active',)
  search_fields = ('name',)
  date_hierarchy = 'start'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
  list_display = ('name', 'conference', 'sorder')
  list_filter = ('conference',)


@admin.register(SponsorshipLevel)
class SponsorshipLevelAdmin(admin.ModelAdmin):
  list_display = ('name', 'conference', 'cost', 'order')
  list_filter = ('conference',)
  list_editable = ('order',)
  raw_id_fields = ('conference',)


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
  list_display = ('name', 'level', 'contact_name', 'contact_phone',
                  'contact_email', 'link', 'active')
  list_filter = ('level', 'active')
  list_editable = ('active',)
  raw_id_fields = ('level',)


@admin.register(Session)
class SessionAdmin(CSVAdminMixin, admin.ModelAdmin):
  list_select_related = ('user',)
  list_display = ('name', 'conference', 'user', 'full_name', 'email', 'stype',
                  'level', 'start', 'duration', 'room', 'all_rooms',
                  'video_url', 'status')
  csv_rows = ('id', 'name', 'conference', 'user', 'full_name', 'email', 'stype',
              'level', 'start', 'duration', 'status', 'admin_link', 'user_link')
  list_filter = ('conference', 'room', 'stype', 'level', 'status')
  date_hierarchy = 'start'
  list_editable = ('room', 'all_rooms', 'video_url', 'status', 'start')
  raw_id_fields = ('user',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
  list_display = ('to', 'name', 'amount', 'paid_on', 'sent', 'Send', 'Payment')
  list_filter = ('paid_on',)
  date_hierarchy = 'sent'
  exclude = ('key',)

  def save_model(self, request, obj, form, change):
    if not obj.key:
      while 1:
        m = hashlib.md5()
        m.update(obj.to.encode('utf-8'))
        m.update(obj.text.encode('utf-8'))
        m.update(obj.subject.encode('utf-8'))
        m.update(datetime.datetime.now().strftime("'%Y-%m-%d %H:%M:%S.%f")
                 .encode('utf-8'))
        m.update(str(random.randint(0, 100000000)).encode('utf-8'))
        key = m.hexdigest()
        if Invoice.objects.filter(key=key).count() == 0:
          break

      obj.key = key

    obj.save()

  def get_urls(self):
    from django.conf.urls import url

    def wrap(view):

      def wrapper(*args, **kwargs):
        return self.admin_site.admin_view(view)(*args, **kwargs)

      return update_wrapper(wrapper, view)

    info = self.model._meta.app_label, self.model._meta.model_name

    urlpatterns = [
        url(r'^(\d+)/send/$', wrap(self.send_view), name='%s_%s_send' % info)
    ]

    urlpatterns += super(InvoiceAdmin, self).get_urls()

    return urlpatterns

  def send_view(self, request, object_id):
    obj = self.get_object(request, object_id)
    obj.send(request)

    return http.HttpResponseRedirect('../../')
