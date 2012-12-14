"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import Client
from .models import EventContainer, Event
from datetime import date, time


class EventTests (TestCase):
    urls = "mezzanine_events.test_urls"
    def setUp(self):
        self.ec = EventContainer.objects.create(
            slug='cont',
        )
        self.ec.save()
        self.event = Event.objects.create(
            slug='cont/blah',
            parent=self.ec,
            date=date.today(),
            start_time=time(9),
            end_time=time(17,30),
            speakers='Fred\nJoe',
            location='1 Susan St\nHindmarsh\nSouth Australia',
            rsvp='By 31 December to aaa@bbb.com',
        )
        self.event.save()
        self.unicode_event = Event.objects.create(
            slug='cont/\u30b5\u30f3\u30b7\u30e3\u30a4\u30f360',
            parent=self.ec,
            title='\xe9\x9d\x9eASCII\xe3\x82\xbf\xe3\x82\xa4\xe3\x83\x88\xe3\x83\xab',
            date=date.today(),
            start_time=time(18),
            end_time=time(23,59),
            location='\u30b5\u30f3\u30b7\u30e3\u30a4\u30f360',
        )
        self.unicode_event.save()
        self.events = (self.event, self.unicode_event)
    
    def test_speakers_list(self):
        self.assertEqual(self.event.speakers_list(), ['Fred', 'Joe'])
    
    def test_clean(self):
        self.event.clean()
        self.assertAlmostEqual(self.event.lat, -34.907924, places=5)
        self.assertAlmostEqual(self.event.lon, 138.567624, places=5)
        self.assertEqual(self.event.mappable_location, '1 Susan St, Hindmarsh SA 5007, Australia')
        
        self.unicode_event.clean()
        self.assertAlmostEqual(self.unicode_event.lat, 35.729534, places=5)
        self.assertAlmostEqual(self.unicode_event.lon, 139.718055, places=5)
        self.assertEqual(self.unicode_event.mappable_location, 'Japan, \u3012170-6090 Tokyo, Toshima, Higashiikebukuro, \uff13\u4e01\u76ee\uff11 \u30b5\u30f3\u30b7\u30e3\u30a4\u30f3\uff16\uff10')
    
    def test_urls(self):
        c = Client()
        for e in self.events:
            r = c.get('/' + e.slug + '/')
            self.assertEqual(r.status_code, 200)
            self.assertTemplateUsed(r, 'pages/event.html')
    
    def test_icalendars(self):
        c = Client()
        for e in self.events:
            r = c.get('/' + e.slug + '/event.ics')
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r['Content-Type'], 'text/calendar')
        
        # test event container calendar
        r = c.get('/cont/calendar.ics')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'text/calendar')
