
from google.appengine.ext import db

class Player(db.Model):
    name = db.StringProperty(required=True)

class Tournament(db.Model):
    season = db.IntegerProperty(default=2)
    date = db.StringProperty(required=True)
    location = db.StringProperty()
    closed = db.BooleanProperty(default=False)

class TournamentData(db.Model):
    player = db.ReferenceProperty(Player)
    tournament = db.ReferenceProperty(Tournament)
    signout_time = db.DateTimeProperty() 
    bounty = db.BooleanProperty(default=False)
    highhand = db.BooleanProperty(default=False)
    badbeat = db.BooleanProperty(default=False)
    signout_order = db.IntegerProperty()
    place = db.IntegerProperty()
    points = db.IntegerProperty(default=0)

class Location(db.Model):
    content = db.StringProperty(multiline=True)

import os
from google.appengine.ext.webapp import template

class Link:  
  def __init__(self, name, url=None):
    self.name = name
    self.url = url
    if url is None:
      self.url = '/' + name.lower()
    self.active = ""

LINKS = [ 
  Link("Home", "/"),
  Link("Players"),
  Link("Tournaments"),
  Link("Rules"),
  Link("Manage")
]

def render(request, response, page, args): 
  fullpath = os.path.join(os.path.dirname(__file__), '../templates/%s.html' % page)

  args['page'] = request.path
  args['links'] = LINKS

  return template.render(fullpath, args)

def get_sorted_players():
  pquery = Player.all()
  players = dict()
  for player in pquery:
    players[player.key().id()] = {'name': player.name, 'id': player.key().id(), 'points': 0, 'p': player} 

  dquery = TournamentData.all()
  for d in dquery:
    if d.tournament.closed:
      players[d.player.key().id()]['points'] += d.points
   
  def sort_by_points(x, y): 
    return int(y['points'] - x['points'])
  sorted_players = sorted(players.values(), sort_by_points) 

  return sorted_players

