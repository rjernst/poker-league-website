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
import json
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache

from handlers.shared import Tournament, TournamentData, Player, render

class AddTournament(webapp.RequestHandler):

  def post(self):
    date = self.request.get('tournament.date') 
    location = self.request.get('tournament.location') 
    logging.info("Adding tournament, date=%s, loc=%s", date, location)
    tournament = Tournament(date=date, location=location)
    key = tournament.put()
    logging.info("Tournament added with id: %s", key.id())
    
    self.response.out.write('%d' % key.id());
    memcache.delete('manage')

class DeleteTournament(webapp.RequestHandler):

  def post(self):
    tid = int(self.request.get('id')) 
    logging.info("Deleting tournament %d", tid)
    tournament = Tournament.get_by_id(tid)
    tournament.delete()
    
    self.response.out.write('/manage');
    memcache.delete('manage')

class Reset(webapp.RequestHandler):

  def post(self):
    tid = int(self.request.get('id')) 
    logging.info("Reseting tournament %d", tid)
    t = Tournament.get_by_id(tid)
    dquery = TournamentData.gql("WHERE tournament = :1", t)
    for d in dquery:
      d.delete()
    
    self.response.out.write('/manage');
    memcache.delete('manage')

class Signout(webapp.RequestHandler):

  def post(self):
    name = self.request.get('player.name')
    tid = int(self.request.get('tournament.id'))
    logging.info('Logging out player %s for tournament id %d', name, tid)

    player = Player.gql('WHERE name = :1', name).fetch(1)[0]
    tournament = Tournament.get_by_id(tid)
    data = TournamentData(player=player, tournament=tournament, 
                          signout_time=datetime.now())
    data.put()

    self.response.out.write(name);


class Close(webapp.RequestHandler):

  def post(self):
    """ Calculate final data for a tournament

        1. places: 1st=5, 2nd=3, 3rd=2, 4th=1
        2. total points (bounty(5) + highhand(5) + badbeat(2) +
                         signout order + place)
    """ 
    tid = int(self.request.get("tournament.id"))
    bounty_name = self.request.get("bounty.name")
    highhand_name = self.request.get("highhand.name")
    badbeat_name = self.request.get("badbeat.name")

    t = Tournament.get_by_id(tid)
    query = TournamentData.gql("WHERE tournament = :1 ORDER BY signout_time", t)

    players = []
    for data in query:
      players.append(data)
      data.signout_order = len(players)
      data.points = data.signout_order

      data.highhand = data.player.name == highhand_name
      if data.highhand:
        data.points += 5

      data.badbeat = data.player.name == badbeat_name
      if data.badbeat:
        data.points += 2

      data.bounty = data.player.name == bounty_name
      if data.bounty:
        data.points += 5

    players[-1].points += 5   # 1st place
    players[-1].place = 1
    players[-2].points += 3   # 2nd place
    players[-2].place = 2
    players[-3].points += 2   # 3rd place
    players[-3].place = 3
    players[-4].points += 1   # 4th place
    players[-4].place = 4

    for data in players:
      data.put()
    t.closed = True
    t.put()

    self.redirect("/tournaments")
    memcache.flush_all()

class EditTournament(webapp.RequestHandler):
  def get(self):
    r = {}

    tid = int(self.request.get('id'))
    logging.info("Edit starting for tournament %d", tid)
    tournament = Tournament.get_by_id(tid)
    r['id'] = tid
    r['date'] = tournament.date
    r['location'] = tournament.location
  
    pquery = Player.all();
    players = []
    for p in pquery:
      players.append(p.name)
    r['players'] = players
    logging.info('Found %d players possible for tournament', len(players))

    dquery = TournamentData.gql('WHERE tournament = :1 ORDER BY signout_time', tournament)
    data = []
    for d in dquery:
      data.append(d.player.name)
    r['data'] = data
    logging.info('Found %d current players for tournament', len(data))

    self.response.out.write(json.dumps(r))

class ViewTournaments(webapp.RequestHandler):
  def get(self):
    tid = self.request.get('id')
    if tid is None:
      ckey = 'tournaments'
    else:
      ckey = 'tournament_%s' % tid
    data = memcache.get(ckey)

    if data is None:
      args = {}
      if tid:
        # view a specific tournament
        page = 'tournament'
        tournament = Tournament.get_by_id(int(tid))
      else:
        tl = Tournament.gql('WHERE closed = True ORDER BY date DESC').fetch(1)
        tournament = tl[0] if len(tl) > 0 else None

      page ='tournaments'
      args['tournament'] = tournament 
      args['data'] = TournamentData.gql('WHERE tournament = :1 \
                                         ORDER BY points DESC' , 
                                        args['tournament'])
      args['tournaments'] = Tournament.gql('WHERE closed = :1 ORDER BY date DESC', True)

      data = render(self.request, self.response, page, args)
      memcache.set(ckey, data)

    self.response.out.write(data)

app = webapp.WSGIApplication([('/manage/tournament/close', Close),
                              ('/manage/tournament/signout', Signout),
                              ('/manage/tournament/reset', Reset),
                              ('/manage/tournament/delete', DeleteTournament),
                              ('/manage/tournament/add', AddTournament),
                              ('/manage/tournament/edit', EditTournament),
                              ('/tournaments.*', ViewTournaments)],
                              debug=True)

