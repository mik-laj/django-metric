import re
from datetime import datetime
from unittest import skipUnless


from dateutil.rrule import MONTHLY, WEEKLY
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.test import TestCase


from .factories import ItemFactory, ValueFactory
from .utils import DATE_FORMAT_MONTHLY, DATE_FORMAT_WEEKLY, GapFiller

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def polyfill_http_response_json():
    try:
        getattr(HttpResponse, 'json')
    except AttributeError:
        import json
        setattr(HttpResponse, 'json', lambda x: json.loads(x.content))


class GapFillerTestCase(TestCase):
    def setUp(self):
        self.date_key = 'date'

    def test_single_month_gap(self):
        qs = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-03", 'param': 3}
        ]

        gf = GapFiller(qs, MONTHLY, self.date_key, DATE_FORMAT_MONTHLY)

        result = gf.fill_gaps()
        expected = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-02", 'param': 0},
            {'date': "2015-03", 'param': 3}
        ]
        self.assertEqual(result, expected)

    def test_single_week_gap(self):
        qs = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-03", 'param': 3}
        ]

        gf = GapFiller(qs, WEEKLY, self.date_key, DATE_FORMAT_WEEKLY)

        result = gf.fill_gaps()
        expected = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-02", 'param': 0},
            {'date': "2015-03", 'param': 3}
        ]
        self.assertEqual(result, expected)

    def test_multiple_month_gaps(self):
        qs = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-03", 'param': 3},
            {'date': "2015-07", 'param': 7}
        ]

        gf = GapFiller(qs, MONTHLY, self.date_key, DATE_FORMAT_MONTHLY)

        result = gf.fill_gaps()
        expected = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-02", 'param': 0},
            {'date': "2015-03", 'param': 3},
            {'date': "2015-04", 'param': 0},
            {'date': "2015-05", 'param': 0},
            {'date': "2015-06", 'param': 0},
            {'date': "2015-07", 'param': 7}
        ]
        self.assertEqual(result, expected)

    def test_no_gaps(self):
        qs = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-02", 'param': 0},
            {'date': "2015-03", 'param': 3}
        ]

        gf = GapFiller(qs, WEEKLY, self.date_key, DATE_FORMAT_WEEKLY)

        result = gf.fill_gaps()
        expected = [
            {'date': "2015-01", 'param': 1},
            {'date': "2015-02", 'param': 0},
            {'date': "2015-03", 'param': 3}
        ]
        self.assertEqual(result, expected)

    def test_empty_qs(self):
        qs = []
        gf = GapFiller(qs, WEEKLY, self.date_key, DATE_FORMAT_WEEKLY)

        result = gf.fill_gaps()
        expected = []
        self.assertEqual(result, expected)

    def test_multiple_params(self):
        qs = [
            {'date': "2015-01", 'a': 1, 'b': 1},
            {'date': "2015-03", 'a': 3, 'b': 4}
        ]

        gf = GapFiller(qs, MONTHLY, self.date_key, DATE_FORMAT_MONTHLY)

        result = gf.fill_gaps()
        expected = [
            {'date': "2015-01", 'a': 1, 'b': 1},
            {'date': "2015-02", 'a': 0, 'b': 0},
            {'date': "2015-03", 'a': 3, 'b': 4}
        ]
        self.assertEqual(result, expected)

    def test_one_element(self):
        qs = [
            {'date': "2015-01", 'param': 1}
        ]

        gf = GapFiller(qs, MONTHLY, self.date_key, DATE_FORMAT_MONTHLY)

        result = gf.fill_gaps()
        expected = [
            {'date': "2015-01", 'param': 1}
        ]
        self.assertEqual(result, expected)


class ValueBrowseListViewTestCase(TestCase):
    def setUp(self):
        self.obj = ItemFactory()
        self.values = ValueFactory.create_batch(size=10, item=self.obj)
        self.url = reverse('metric:item_detail', kwargs={'key': self.obj.key,
                                                        'month': str(self.values[0].time.month),
                                                        'year': str(self.values[0].time.year),
                                                        })

    def test_valid_status_code_for_detail_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "Invalid status code on '{}'".format(self.url))

    def test_output_contains_values(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.values[0].value)

    def test_output_contains_description(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.obj.description)


class CSVValueListViewTestCase(TestCase):
    def setUp(self):
        self.obj = ItemFactory()
        self.values = ValueFactory.create_batch(size=10, item=self.obj)
        self.url = reverse('metric:item_detail_csv', kwargs={'key': self.obj.key,
                                                            'month': self.values[0].time.month,
                                                            'year': self.values[0].time.year,
                                                            })

    def test_valid_status_code_for_detail_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "Invalid status code on '{}'".format(self.url))

    def test_output_contains_values(self):
        response = self.client.get(self.url)
        self.assertContains(response, str(self.values[0].value))

    def test_output_contains_item_name(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.obj.name)


class JSONValueListViewTestCase(TestCase):
    def setUp(self):
        self.obj = ItemFactory()
        self.values = ValueFactory.create_batch(size=10, item=self.obj)
        self.url = reverse('metric:item_detail_json', kwargs={'key': self.obj.key,
                                                             'month': self.values[0].time.month,
                                                             'year': self.values[0].time.year,
                                                             })

    def test_valid_status_code_for_detail_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "Invalid status code on '{}'".format(self.url))

    def test_output_contains_values(self):
        response = self.client.get(self.url).json()
        sorted(self.values, key=lambda x: x.time)
        self.assertEqual(response['values'][0]['value'], self.values[0].value)

    def test_output_contains_item_name(self):
        response = self.client.get(self.url).json()
        self.assertEqual(response['item']['name'], self.obj.name)


class TestManagementCommand(TestCase):
    def test_command_no_raises_exception(self):
        call_command('update_metric')

    def test_command_outputs(self):
        out = StringIO()
        call_command('update_metric', stdout=out)
        output = out.getvalue()
        self.assertTrue(re.search("Registered .* new items", output))
        self.assertTrue(re.search("Registered .* values.", output))
