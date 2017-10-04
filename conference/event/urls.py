from django.conf.urls import include, url

from conference.event.views import invoice

urlpatterns = [
    url(r'^invoice/(\S+)/$',
        invoice,
        name='conference-invoice'),
]