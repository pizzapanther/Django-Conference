import csv
import codecs
import io
import types
import csv
import random

import requests

from django import http
from django.utils import timezone
from django.conf import settings

class Randomizer:
  def __init__ (self, checked_in=True):
    print('Retrieving checked in users from EventBrite')
    self.peeps = attendees(checked_in)
    self.count = 1
    random.shuffle(self.peeps)
    
  def winner (self):
    print('{}: {}'.format(self.count, self.peeps.pop()))
    self.count += 1
    
def attendees(checked_in=True):
  page = 1
  peeps = []

  while 1:
    data = attendee_data(page)

    for attendee in data['attendees']:
      if checked_in:
        if attendee['checked_in'] and attendee['profile']['name'] not in peeps:
          peeps.append(attendee['profile']['name'])
          
      elif attendee['profile']['name'] and attendee['profile']['name'] not in peeps:
        peeps.append(attendee['profile']['name'])

    if data['pagination']['page_count'] == data['pagination']['page_number']:
      break

    else:
      page = page + 1

  return peeps
  
def attendee_data(page=1):
  url = '{}/events/{}/attendees/'.format(settings.EVENTBRITE_API_URL,
                                         settings.EVENTBRITE_EVENT_ID)
  params = {'token': settings.EVENTBRITE_OAUTH_TOKEN, 'page': page}

  response = requests.get(url, params=params)

  return response.json()
  
class CSVFileGenerator(object):
  mimeType = 'text/csv'
  queryset = None
  tags = []

  def __init__(self, queryset, tags, filename=None):
    self.queryset = queryset
    self.tags = tags
    if filename:
      self.filename = filename

    else:
      self.filename = self.queryset[0]._meta.object_name

  def generate(self):
    fh = io.StringIO()
    writer = csv.writer(fh)
    writer.writerow(self.tags)
    for item in self.queryset:
      current_row = []

      for tag in self.tags:
        value = getattr(item, tag)

        if callable(value):
          value = value()

        value = "{}".format(value)
        current_row.append(value)

      writer.writerow(current_row)

    return fh.getvalue()

  def getFileName(self):
    return self.filename + timezone.now().strftime("_%Y%m%d%H%M%S") + '.csv'

  def getIteratorResponse(self):
    response = http.HttpResponse(self.generate(), content_type=self.mimeType)
    response[
        'Content-Disposition'] = 'attachment; filename=' + self.getFileName()
    return response
