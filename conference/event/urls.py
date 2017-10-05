from django.conf.urls import include, url

from conference.event.views import invoice
from conference.views import conference_data

urlpatterns = [
    url(r'^invoice/(\S+)/$',
        invoice,
        name='conference-invoice'),
    url(r'^data/(\S+).json$',
        conference_data,
        name='conference-data'),
]