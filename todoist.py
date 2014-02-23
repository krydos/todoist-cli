#!/usr/bin/python
import urllib2
import json
import colortrans
import sys

class Todoist:

    token = "<TOKEN FROM TODOIST USER SETTINGS MENU"
    todoist_api_url = "http://todoist.com/API/"

    """ get all project """
    def getProjects(self):
        req = urllib2.Request(self.todoist_api_url + 'getProjects?token=' + self.token)
        response = urllib2.urlopen(req)
        return response.read()

    """ get all tasks """
    def getUncompletedTasks(self):
        # TODO done with this function
        pass


class IOformat:

    """ print text in color """
    def print_in_color(self, color, text):
        print '\033[48;5;' + color + 'm' + text

    """ hex color to bash color"""
    def hex2bash(self, hex_color):
        return colortrans.rgb2short(hex_color)



# create objects
todoist = Todoist()
io = IOformat()

# argument list
arguments = sys.argv[1:]

try:

    # if user want to get list of all projects
    if arguments[0] == 'p':
        if arguments[1] == 'ls':
            json_projects = json.loads(todoist.getProjects())

            for project in json_projects:
                io.print_in_color(io.hex2bash(project['color'])[0], project['name'])

    # if user want to get list of all tasks
    if arguments[0] == 'ls':
        # TODO get all uncompleted tasks
        pass

except IndexError:
    print 'Something wrong with arguments'


