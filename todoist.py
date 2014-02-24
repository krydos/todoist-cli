#!/usr/bin/python
import urllib2
import json
import colortrans
import sys
import todoist_functions

COLOR_OUTPUT = False

class Todoist:

    #token = "<TOKEN FROM TODOIST USER SETTINGS MENU"
    token = "c067009bfb0ca72c2dcc90d88ad0a777a9d8cadd"
    todoist_api_url = "http://todoist.com/API/"

    """ get all project """
    def getProjects(self):
        t = todoist_functions.ToDoIst(token=self.token)
        return t.getProjects();

    """ get all tasks """
    def getUncompletedTasks(self, project_id):
        t = todoist_functions.ToDoIst(token=self.token)
        return t.getUncompletedItems(project_id);

    """ get all tasks for today """
    def getTodayTasks(self):
        t = todoist_functions.ToDoIst(token=self.token)
        #TODO get today tasks
        return t.query({"tod"});

    """ get all tasks for tomorrow """
    def getTomTasks(self):
        return self._do_get_request(self.todoist_api_url + 'query?token=' + self.token + '&queries=["tom"]')

    """ get all tasks for 7 days """
    def get7dTasks(self):
        pass

    """ get all tasks for query """
    def getQueryTasks(self, query):
        return self._do_get_request(self.todoist_api_url + 'query?token=' + self.token + '&queries=['+query+']')

    def _do_get_request(self, address):
        req = urllib2.Request(address)
        response = urllib2.urlopen(req)
        return response.read()


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

# check on color output
for arg in sys.argv:
    if arg == '-c':
        COLOR_OUTPUT = True

try:

    # if user want to get list of all projects
    if arguments[0] == 'p':
        if arguments[1] == 'ls':
            json_projects = todoist.getProjects()

            for project in json_projects:
                if COLOR_OUTPUT == True:
                    io.print_in_color(io.hex2bash(project['color'])[0], project['name'])
                else:
                    print project['name']


    # if user want to get list of all tasks
    if arguments[0] == 'ls' and len(arguments) == 1:
        json_projects = todoist.getProjects()
        for project in json_projects:
            json_tasks = todoist.getUncompletedTasks(project['id'])

            for task in json_tasks:
                if COLOR_OUTPUT == True:
                    io.print_in_color(io.hex2bash(project['color'])[0], task['content'] + ' ('+ project['name'] +')')
                    print "\n"
                else:
                    print task['content'] + ' ('+ project['name'] +')'
                    print "\n"

    # if user want to get list of all tasks for today
    if arguments[0] == 'ls' and len(arguments) == 2:
        if arguments[1] == 'tod':
            json_tasks = json.loads(todoist.getTodayTasks())
            json_tasks = json_tasks[0]['data']
            for task in json_tasks:
                print task['content']
                print "\n"

        if arguments[1] == 'tom':
            json_tasks = json.loads(todoist.getTomTasks())
            json_tasks = json_tasks[0]['data']
            for task in json_tasks:
                print task['content']
                print "\n"

        if arguments[1] == '7d':
            json_tasks = json.loads(todoist.get7dTasks())
            json_tasks = json_tasks[0]['data']
            for task in json_tasks:
                print task['content']
                print "\n"

    if arguments[0] == 'q':
        json_tasks = json.loads(todoist.getQueryTasks(arguments[1]))
        json_tasks = json_tasks[0]['data']
        for task in json_tasks:
            print task['content']
            print "\n"


except IndexError:
    print 'Something wrong with arguments'


