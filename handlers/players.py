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
from google.appengine.ext import db
from google.appengine.api import memcache

from handlers.shared import Player, TournamentData, Tournament, render, get_sorted_players

class AddPlayer(webapp.RequestHandler):

  def post(self):
    name = self.request.get('player.name') 
    player = Player(name=name)
    player.put()

    self.redirect('/manage')
    memcache.delete('manage')

class ViewPlayers(webapp.RequestHandler):
  def get(self):
    pid = self.request.get('id')
    if pid is None:
      ckey = 'players'
    else:
      ckey = 'player_%s' % pid
    data = memcache.get(ckey)

    if data is None:
      args = {}
      selected_player = None
      sorted_players = get_sorted_players()
      for p in sorted_players:
        if pid and int(pid) == p['id']:
          selected_player = p
        logging.info("%s(%d) = %d", p['name'], p['id'], p['points'])

      if selected_player is None:
        selected_player = sorted_players[0]

      logging.info('selected player %s', selected_player)

      args['data'] = TournamentData.gql('WHERE player = :1', selected_player['p'])
      args['player'] = selected_player
      args['players'] = sorted_players 

      data = render(self.request, self.response, 'players', args) 
      memcache.set(ckey, data)
    else:
      logging.info("Cache hit: %s", ckey)
      logging.info(memcache.get_stats())

    self.response.out.write(data)

app = webapp.WSGIApplication([('/manage/players/add', AddPlayer),
                              ('/players.*', ViewPlayers)],
                              debug=True)

