import urllib, urllib2
import json
import dateutil.parser

class ArgumentExpected(Exception):
    pass
class ServerError(Exception):
    pass
class UnexpectedResult(Exception):
    pass

class Processors:
    @staticmethod
    def bool2int(value):
        return value if not isinstance(value,bool) else int(value)

    @staticmethod
    def str2date(value):
        return dateutil.parser.parser().parse(value)
#Processors=_Processors()

class ToDoIst:
    def __init__(self, email=None, password=None, token=None,
        base_url="todoist.com/API",
        sync_url="todoist.com/TodoistSync",
    ):
        self.email = email
        self.password = password
        self.token = token
        self.base_url = base_url
        self.sync_url = sync_url

    def login(self, email=None, password=None):
        if email:
            self.email = email
        if password:
            self.password = password
        if not self.email or not self.password:
            raise Exception("oops") # TODO: more precise error

        res = self._fetch("login", dict(email=self.email, password=self.password), dict(premium_until=Processors.str2date), token_field=None, POST=True)
        self.token = res["api_token"]
        return res

    def getTimezones(self):
        return self._fetch("getTimezones", dict(), token_field=None)
    def register(self, email, fullname, password, timezone):
        return self._fetch("register", dict(email=email, fullname=fullname, password=password, timezone=timezone), dict(premium_until=Processors.str2date), token_field=None, POST=True)
    def updateUser(self, email=None, full_name=None, password=None, timezone=None, date_format=None, time_format=None, start_page=None):
        return self._fetch("updateUser", dict(email=email, full_name=full_name, password=password, timezone=timezone, date_format=date_format, time_format=time_format, start_page=start_page), POST=True)

    def getProjects(self):
        return self._fetch("getProjects", dict())
    def getProject(self, project_id):
        return self._fetch("getProject", dict(project_id=project_id))
    def addProject(self, name, color=None, indent=None, order=None):
        return self._fetch("addProject", dict(name=name, color=color, indent=indent, order=order))
    def updateProject(self, project_id, name=None, color=None, indent=None, order=None, collapsed=None):
        return self._fetch("updateProject", dict(project_id=project_id, name=name, color=color, indent=indent, order=order, collapsed=collapsed))
    def updateProjectOrders(self, item_id_list):
        return self._fetch("updateProjectOrders", dict(item_id_list=item_id_list))
    def deleteProject(self, project_id):
        return self._fetch("deleteProject", dict(project_id=project_id))

    def getLabels(self, project_id, as_list=None):
        return self._fetch("getLabels", dict(project_id=project_id, as_list=Processors.bool2int(as_list)))
    def addLabel(self, name, color=None):
        return self._fetch("addLabel", dict(name=name, color=color))
    def updateLabel(self, old_name, new_name):
        return self._fetch("updateLabel", dict(old_name=old_name, new_name=new_name))
    def updateLabelColor(self, name, color):
        return self._fetch("updateLabelColor", dict(name=name, color=color))
    def deleteLabel(self, name):
        return self._fetch("deleteLabel", dict(name=name))

    def getUncompletedItems(self, project_id):
        return self._fetch("getUncompletedItems", dict(project_id=project_id), dict(due_date=Processors.str2date))
    def getAllCompletedItems(self, project_id=None, label=None, interval=None):
        return self._fetch("getAllCompletedItems", dict(project_id=project_id, label=label, interval=interval), dict(due_date=Processors.str2date))
    def getCompletedItems(self, project_id):
        return self._fetch("getCompletedItems", dict(project_id=project_id), dict(due_date=Processors.str2date))
    def getItemsById(self, ids):
        return self._fetch("getItemsById", dict(ids=ids), dict(due_date=Processors.str2date))
    def addItem(self, project_id, content, date_string=None, priority=None, indent=None, item_order=None):
        return self._fetch("addItem", dict(project_id=project_id, content=content, date_string=date_string, priority=priority, indent=indent, item_order=item_order), dict(due_date=Processors.str2date))
    def updateItem(self, id, content=None, date_string=None, priority=None, indent=None, item_order=None, collapsed=None):
        return self._fetch("updateItem", dict(id=id, content=content, date_string=date_string, priority=priority, indent=indent, item_order=item_order, collapsed=collapsed), dict(due_date=Processors.str2date))
    def updateOrders(self, project_id, item_id_list):
        return self._fetch("updateOrders", dict(project_id=project_id, item_id_list=item_id_list))
    def moveItems(self, project_items, to_project):
        return self._fetch("moveItems", dict(project_items=project_items, to_project=to_project))
    def updateRecurringDate(self, ids):
        return self._fetch("updateRecurringDate", dict(ids=ids), dict(due_date=Processors.str2date))
    def deleteItems(self, ids):
        return self._fetch("deleteItems", dict(ids=ids))
    def completeItems(self, ids, in_history=None):
        return self._fetch("completeItems", dict(ids=ids, in_history=Processors.bool2int(in_history)))
    def uncompleteItems(self, ids):
        return self._fetch("uncompleteItems", dict(ids=ids))

    def addNote(self, item_id, content):
        return self._fetch("addNote", dict(item_id=item_id, content=content))
    def updateNote(self, note_id, content):
        return self._fetch("updateNote", dict(note_id=note_id, content=content))
    def deleteNote(self, item_id, note_id):
        return self._fetch("deleteNote", dict(item_id=item_id, note_id=note_id))
    def getNotes(self, item_id):
        return self._fetch("getNotes", dict(item_id=item_id))

    def query(self, queries, as_count=None):
        return self._fetch("query", dict(queries=queries, as_count=Processors.bool2int(as_count)))

    def sync_get(self, projects_timestamps=None):
        return self._fetch("get", dict(projects_timestamps=projects_timestamps), token_field=None, POST=True)
    def sync_sync(self, items):
        return self._fetch("sync", dict(items=items), token_field=None, POST=True)

    def _fetch(self, action, args=None, postprocessors={}, POST=False, token_field="token", url=None):
        url = "https://%s/%s" % (self.base_url if not url else getattr(self,url), action)
        if args is None:
            args = {}

        def connect():
            if POST and token_field:
                args[token_field] = self.token
            s_args = urllib.urlencode(args)
            #print url
            #print s_args

            if POST:
                return urllib2.urlopen(url,s_args)
            else:
                return urllib2.urlopen("%s?%s" % (url,s_args),urllib.urlencode({token_field:self.token}))

        try:
            try:
                res = connect()
            except urllib2.HTTPError as e:
                if e.code == 401:
                    self.login()
                    res = connect()
                else:
                    raise

        except urllib2.HTTPError as e:
            raise Exception("HTTP Error: %s" % e.code)
        except urllib2.URLError as e:
            raise Exception("URL Error: %s" % e.reason)


        res = res.read()

        try:
            res = json.loads(res)
        except:
            raise UnexpectedResult(res)

        if isinstance(res,str):
            if res == "ok":
                return True
            raise ServerError(res)
        if postprocessors:
            if isinstance(res,list):
                flag = False
            elif isinstance(res,dict):
                flag = True
                res = [res]
            else:
                raise UnexpectedResult(res)
            for i in res:
                if not isinstance(i,dict):
                    raise UnexpectedResult(res)
                for k,v in postprocessors.items():
                    if k in i.keys():
                        try:
                            i[k] = v(i[k])
                        except:
                            pass
            if flag:
                res = res[0]
        return res
