import csv
import json
from collections import OrderedDict
from datetime import datetime

from braces.views import (JSONResponseMixin)
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.datetime_safe import date
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View

from .models import Item, Value, Graph


class ApiListViewMixin(JSONResponseMixin):
    def get(self, request, *args, **kwargs):
        return self.render_json_response(self.get_object_list())


class MetricIndexView(TemplateView):
    template_name = 'metric/index.html'

    def get_context_data(self, **kwargs):
        kwargs['item_list'] = Item.objects.for_user(self.request.user).all()
        kwargs['graph_list'] = Graph.objects.all()
        return super(MetricIndexView, self).get_context_data(**kwargs)


class TimeMixin(object):
    @property
    def today(self):
        today = date.today()
        return today.replace(day=1,
                             month=int(self.kwargs.get('month', str(today.month))),
                             year=int(self.kwargs.get('year', str(today.year))))

    @property
    def start(self):
        return self.today.replace(day=1)

    @property
    def end(self):
        return self.today.replace(day=1) + relativedelta(months=1)


class ValueListView(TimeMixin):
    @property
    def item(self):
        return get_object_or_404(Item.objects.for_user(self.request.user),
                                 key=self.kwargs['key'])

    def get_queryset(self):
        return Value.objects.filter(time__lte=self.end, time__gte=self.start).filter(item=self.item).all()


class ValueBrowseListView(ValueListView, TemplateView):
    template_name = "stats/item_details.html"

    def get_context_data(self, **kwargs):
        item = self.item
        kwargs['item'] = item
        kwargs['value_list'] = self.get_queryset()
        kwargs['today'], kwargs['start'], kwargs['end'] = self.today, self.start, self.end
        return super(ValueBrowseListView, self).get_context_data(**kwargs)


class CSVValueListView(ValueListView, View):
    def get(self, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(self.item.key)
        writer = csv.writer(response)
        writer.writerow([_("Key"), _("Name"), _("Time"), _("Time (unix)"), _("Value")])
        for item in self.get_queryset():
            writer.writerow([self.item.key.encode('utf-8'),
                             self.item.name.encode('utf-8'),
                             item.time.strftime("%c"),
                             item.time.strftime("%s"),
                             item.value])
        return response


class JSONValueListView(ValueListView, View):
    def get(self, *args, **kwargs):
        response = HttpResponse(content_type='application/json')
        data = {'item': self.item.as_dict(),
                'values': [o.as_dict() for o in self.get_queryset()]}
        json.dump(data, response, indent=4)
        return response


class GraphTimeMixin(TimeMixin):
    @property
    def object(self):
        if not getattr(self, '_object', None):
            values_qs = Value.objects.filter(time__lte=self.end, time__gte=self.start).all()
            prefetch_obj = Prefetch('items__value_set', values_qs)
            graph_qs = Graph.objects.prefetch_related('items').prefetch_related(prefetch_obj).all()
            self._object = get_object_or_404(graph_qs, pk=self.kwargs['pk'])
        return self._object

    def get_dataset(self, item, times):
        values = {value.time.strftime("%s"): value.value for value in item.value_set.all()}
        data = [values.get(time, None) for time in times]
        label = item.name
        return {'data': data, 'label': label}

    @property
    def times(self):
        if not getattr(self, '_times', None):
            self._times = list({value.time.strftime("%s")
                                for item in self.object.items.all()
                                for value in item.value_set.all()})
            self._times = sorted(self._times)
        return self._times

    def get_graph(self):
        dataset = [self.get_dataset(item, self.times) for item in self.object.items.all()]
        labels = [str(datetime.fromtimestamp(int(time))) for time in self.times]
        return {'datasets': dataset, 'labels': labels}

    def get_table(self):
        header = [item.as_dict() for item in self.object.items.all()]
        data = {}
        for item in self.object.items.all():
            for value in item.value_set.all():
                if item.key not in data:
                    data[item.key] = {}
                data[item.key][value.time.strftime("%s")] = value.value
        body = []
        for time in self.times:
            data_row = OrderedDict((item['key'], data[item['key']].get(time, None)) for item in header)
            body.append({'date': time,
                         'label': str(datetime.fromtimestamp(int(time))),
                         'row': data_row})
        return {'header': header, 'body': body}


class GraphDetailView(GraphTimeMixin, TemplateView):
    template_name = "stats/graph_details.html"

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        kwargs['today'], kwargs['start'], kwargs['end'] = self.today, self.start, self.end
        kwargs['graph'] = self.get_graph()
        kwargs['table'] = self.get_table()
        return super(GraphDetailView, self).get_context_data(**kwargs)


class JSONGraphDetailView(GraphTimeMixin, View):
    def get(self, *args, **kwargs):
        response = HttpResponse(content_type='application/json')
        json.dump(self.get_table(), response, indent=4)
        return response
