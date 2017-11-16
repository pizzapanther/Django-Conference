from django.conf.urls import include, url

from conference.event.views import invoice
from conference.views import conference_data, pyvideo

urlpatterns = [
    url(r'^invoice/(\S+)/$', invoice, name='conference-invoice'),
    url(r'^pyvideo/(\S+).json$', pyvideo, name='conference-pyvideo'),
    url(r'^data/(\S+).json$', conference_data, name='conference-data'),
]
