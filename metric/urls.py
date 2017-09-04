from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(r'^$', views.MetricIndexView.as_view(),
        name="index"),
    url(_(r'^item-(?P<key>[\w\-.]+)/$'), views.ValueBrowseListView.as_view(),
        name="item_detail"),
    url(_(r'^item-(?P<key>[\w\-.]+)/(?P<month>\d+)/(?P<year>\d+)/~csv$'), views.CSVValueListView.as_view(),
        name="item_detail_csv"),
    url(_(r'^item-(?P<key>[\w\-.]+)/(?P<month>\d+)/(?P<year>\d+)/~json$'), views.JSONValueListView.as_view(),
        name="item_detail_json"),
    url(_(r'^item-(?P<key>[\w\-.]+)/(?P<month>\d+)/(?P<year>\d+)$'), views.ValueBrowseListView.as_view(),
        name="item_detail"),
    url(_(r'^graph-(?P<pk>\d+)$'), views.GraphDetailView.as_view(),
        name="graph_detail"),
    url(_(r'^graph-(?P<pk>\d+)/(?P<month>\d+)/(?P<year>\d+)$'), views.GraphDetailView.as_view(),
        name="graph_detail"),
    url(_(r'^graph-(?P<pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/~json$'), views.JSONGraphDetailView.as_view(),
        name="graph_detail_json"),
]
