from django.conf.urls import handler404, handler500, include, url
from django.contrib import admin
from django.contrib.auth.views import logout

import metric.urls

__all__ = ['handler404', 'handler500']


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^metric/', (metric.urls.urlpatterns, 'metric', 'metric'))
]