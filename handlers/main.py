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

from handlers.shared import Player, TournamentData, Tournament, Location, render, get_sorted_players

class MainHandler(webapp.RequestHandler):

  def get(self):
    data = memcache.get('main')
    if data is None:
      args = {}
      args['top_players'] = get_sorted_players()[:3]
      tquery = Tournament.gql('WHERE closed = True ORDER BY date DESC')
      args['recent_tournaments'] = tquery.fetch(3)
      args['location'] = Location.all().get()
      data = render(self.request, self.response, 'home', args) 
      memcache.set('main', data)
    
    self.response.out.write(data)

app = webapp.WSGIApplication([('/.*', MainHandler)],
                              debug=True)
