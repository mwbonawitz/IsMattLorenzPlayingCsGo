import os
import sys
import requests
import json
from flask import Flask
from pyquery import PyQuery as pq


app = Flask(__name__)


@app.route("/")
def is_matt_lorenz_playing_cs():
	matt_lorenz = MattLorenz()
	is_playing_cs = matt_lorenz.is_currently_playing_cs()
	steam_name = matt_lorenz.get_steam_name()
	return "Matt lorenz ({1}) {0} playing CS:GO".format("is" if is_playing_cs else "isn't", steam_name)


class SteamStatus(object):
	ONLINE = "Currently Online"
	OFFLINE = "Currently Offline"
	IN_GAME = "Currently In-Game"


class SteamGames(object):
	CSGO = "Counter-Strike: Global Offensive"


class SteamInfo(object):
	def __init__(self, steam_name, currently_playing):
		self.steam_name = steam_name
		self.currently_playing = currently_playing


class SteamParser(object):
	def __init__(self, id):
		self.id = id
		self.url = "http://steamcommunity.com/profiles/{0}".format(id)

	def get_steam_info(self):
		steam_html = self.__pull_steam_page()
		steam_name = self.__parse_steam_name(steam_html)
		currently_playing = self.__parse_currently_playing(steam_html)
		info = SteamInfo(steam_name, currently_playing)
		return info

	def __pull_steam_page(self):
		print "Getting steam page: [{0}]".format(self.url)
		r = requests.get(self.url)
		return r.text

	def __parse_current_state(self, html):
		html_obj = pq(html)
		current_steam_state = html_obj("div.profile_in_game_header").text()
		if current_steam_state == SteamStatus.IN_GAME:
			return SteamStatus.IN_GAME
		elif current_steam_state == SteamStatus.ONLINE:
			return SteamStatus.ONLINE
		else:
			return SteamStatus.OFFLINE

	def __parse_currently_playing(self, html):
		current_state = self.__parse_current_state(html)
		if current_state == SteamStatus.IN_GAME:
			html_obj = pq(html)
			currently_playing = html_obj("div.profile_in_game_name").text()
			print "Parsed currently playing: '{0}'".format(currently_playing)
			return currently_playing
		return None

	def __parse_steam_name(self, html):
		html_obj = pq(html)
		steam_name = html_obj("span.actual_persona_name").text()
		print "Steam Name: {0}".format(steam_name)
		return steam_name


class SteamPlayer(object):
	def __init__(self, config):
		print "Using config: {0}".format(os.path.abspath(config))
		self.config = self.__load_config(config)
		self.steam_parser = SteamParser(self.config["SteamId"])
		self.steam_info = self.steam_parser.get_steam_info()

	def __load_config(self, config):
		with open(config, 'r') as f:
			contents = f.read()
		return json.loads(contents)

	def get_currently_playing(self):
		return self.steam_info.currently_playing

	def get_steam_name(self):
		return self.steam_info.steam_name

	def is_currently_playing_cs(self):
		currently_playing = self.get_currently_playing()
		steam_name = self.get_steam_name()
		print "{2} ({0}) is playing: '{1}'".format(self.config["Name"], currently_playing, steam_name)
		return currently_playing == SteamGames.CSGO


class MattLorenz(SteamPlayer):
	def __init__(self):
		super(MattLorenz, self).__init__("matt_lorenz.json")


if __name__ == "__main__":
	"""
	matt_lorenz = MattLorenz()
	is_playing_cs = matt_lorenz.is_currently_playing_cs()
	print "Matt lorenz {0} playing CS:GO".format("is" if is_playing_cs else "isn't")
	"""
	app.run()