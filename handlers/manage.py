#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and 
# limitations under the License.
#

import os
import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

from handlers.shared import Player, Tournament, Location, render

class MainHandler(webapp.RequestHandler):

  def get(self):
    data = memcache.get('manage')  
    if data is None:
      players = Player.gql('ORDER BY name')
      tournaments = Tournament.gql('WHERE closed = False ORDER BY date')
      location = Location.all().get()
      data = render(self.request, self.response, 'manage', 
                    {'players': players, 'tournaments': tournaments, 
                     'location': location})
      memcache.set('manage', data)
    self.response.out.write(data)

class LocationHandler(webapp.RequestHandler):

  def post(self):
    content = self.request.get('content')
    location = Location.all().get()
    if location is None:
        location = Location()
    location.content = content
    location.save()
    self.redirect('/manage')
    memcache.flush_all()

app = webapp.WSGIApplication([('/manage/location/update', LocationHandler),
                              ('/manage', MainHandler)],
                              debug=True)

