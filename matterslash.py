#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
This is a very basic server application that receives Mattermost slash commands.
Set up your slash commands as described in http://docs.mattermost.com/developer/slash-commands.html
As a sample, a /weather report using OpenWeatherMaps is included.
Feel free to fork and expand this project.

I struggled a lot with de- and encoding of strings. I suppose, that could be done much easier.
"""

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json
# This is used for /weather command
import pyowm

# The token seems not to be used, as of Mattermost 2.0
MATTERMOST_TOKEN = 'jlaskjDd983zurfhnjkfhz878h'
HOSTNAME = 'localhost'
PORT = 8088

# guarantee unicode string
_u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t


class MattermostRequest:
    """
    This is what we get from Mattermost
    """
    response_url = ''
    text = ''
    token = ''
    channel_id = ''
    team_id = ''
    command = ''
    team_domain = ''
    user_name = ''
    channel_name = ''


class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Respond to a POST request."""

        # Extract the contents of the POST
        length = int(self.headers['Content-Length'])
        post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))

        # Get POST data and initialize MattermostRequest object
        for key, value in post_data.iteritems():
            if key == 'response_url':
                MattermostRequest.response_url = value
            elif key == 'text':
                MattermostRequest.text = value
            elif key == 'token':
                MattermostRequest.token = value
            elif key == 'channel_id':
                MattermostRequest.channel_id = value
            elif key == 'team_id':
                MattermostRequest.team_id = value
            elif key == 'command':
                MattermostRequest.command = value
            elif key == 'team_domain':
                MattermostRequest.team_domain = value
            elif key == 'user_name':
                MattermostRequest.user_name = value
            elif key == 'channel_name':
                MattermostRequest.channel_name = value

        responsetext = ''

        if MattermostRequest.command[0] == u'/weather':
            responsetext = getweather(MattermostRequest.text)
        elif MattermostRequest.command[0] == u'/othercommand':
            responsetext = dosomething(MattermostRequest.text, MattermostRequest.user_name)
        elif MattermostRequest.command[0] == u'/yetanothercommand':
            responsetext = dosomethingelse(MattermostRequest.text, MattermostRequest.user_name)

        if responsetext:
            data = {}
            data['response_type'] = 'ephemeral'
            data['text'] = responsetext

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data))

            # {
            # "response_type": "in_channel",
            # "text": "This is some response text."
            # }
        return


def getweather(city):
    searchstring = ''.join(city).encode('latin1')
    searchstring = searchstring
    if searchstring == '':
        searchstring = 'Kiel,de'

    # Get your own API key from http://openweathermap.org/api
    # You can change the language setting here:
    owm = pyowm.OWM(API_key='skjdjf98423322fjwesjfwefj898jklf', language='en')
    observation = owm.weather_at_place(searchstring)
    w = observation.get_weather()

    city = _u(''.join(city))
    response = '#### You requested the weather in ' + city + ':\n\n'
    response = response + '| Parameter | Value |\n' + \
               '| :---- | :---- |\n'
    response = response + '| Temperature : | ' + str(w.get_temperature('celsius')['temp']) + u"° C |\n"
    response = response + '| Status : | ' + w.get_detailed_status() + " |\n"
    response = response + u'| Clouds: | ' + str(w.get_clouds()) + "% |\n"
    response = response + u'| Wind speed: | ' + str(w.get_wind()['speed']) + " |\n"
    response = response + '| Wind direction: | ' + str(w.get_wind()['deg']) + u"° |\n"
    response = response + '| Air pressure: | ' + str(w.get_pressure()['press']) + " hPa|\n"
    return response


def dosomething(text, username):
    username = ''.join(username).encode('latin1')
    text = ''.join(text).encode('latin1')

    return u'#### Hello ' + username + '!\n This is what you wrote: `' + text + "`."


def dosomethingelse(text, username):
    username = ''.join(username).encode('latin1')
    text = ''.join(text).encode('latin1')

    return u'#### Moin ' + username + ' as we say in northern Germany. What did you mean with `' + text + "`?"


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer

    server = HTTPServer((HOSTNAME, PORT), PostHandler)
    print('Starting matterslash server, use <Ctrl-C> to stop')
    server.serve_forever()
