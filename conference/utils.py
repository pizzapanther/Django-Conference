import csv
import codecs
import io
import types
import csv

from django import http
from django.utils import timezone


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
