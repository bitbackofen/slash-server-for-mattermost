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

# Define server address and port, use localhost if you are running this on your Mattermost server.
HOSTNAME = 'localhost'
PORT = 8088

# guarantee unicode string
_u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t


class MattermostRequest(object):
    """
    This is what we get from Mattermost
    """
    def __init__(self, response_url=None, text=None, token=None, channel_id=None, team_id=None, command=None,
                 team_domain=None, user_name=None, channel_name=None):
        self.response_url = response_url
        self.text = text
        self.token = token
        self.channel_id = channel_id
        self.team_id = team_id
        self.command = command
        self.team_domain = team_domain
        self.user_name = user_name
        self.channel_name = channel_name


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

        # Triggering the token is possibly more failure-resistant:
        # if MattermostRequest.token == 'token1':
        #    do_some_thing()
        # elif MattermostRequest.token == 'token2':
        #    do_some_other_thing()
        # Here we trigger the command
        if MattermostRequest.command[0] == u'/weather':
            responsetext = getweather(MattermostRequest.text)
        elif MattermostRequest.command[0] == u'/othercommand':
            responsetext = dosomething(MattermostRequest.text, MattermostRequest.user_name)
        elif MattermostRequest.command[0] == u'/yetanothercommand':
            responsetext = dosomethingelse(MattermostRequest.text, MattermostRequest.user_name)

        if responsetext:
            data = {}
            # 'response_type' may also be 'in_channel'
            data['response_type'] = 'ephemeral'
            data['text'] = responsetext
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data))
        return


def getweather(city):
    searchstring = ''.join(city).encode('latin1')
    searchstring = searchstring
    if searchstring == '':
        searchstring = 'Kiel,de'

    # Get your own API key from http://openweathermap.org/api
    # You can also change the language setting here:
    owm = pyowm.OWM(API_key='skjdjf98423322fjwesjfwefj898jklf', language='en')
    observation = owm.weather_at_place(searchstring)
    w = observation.get_weather()

    city = _u(''.join(city))
    # Build the response as table...
    response = u'#### You requested the weather in ' + city + ':\n\n'
    response += u'| Parameter | Value |\n' + \
               u'| :---- | :---- |\n'
    response += u'| Temperature : | ' + str(w.get_temperature('celsius')['temp']) + u"° C |\n"
    response += u'| Status : | ' + w.get_detailed_status() + u" |\n"
    response += u'| Clouds: | ' + str(w.get_clouds()) + u"% |\n"
    response += u'| Wind speed: | ' + str(w.get_wind()['speed']) + u" |\n"
    response += u'| Wind direction: | ' + str(w.get_wind()['deg']) + u"° |\n"
    response += u'| Air pressure: | ' + str(w.get_pressure()['press']) + u" hPa|\n"
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
