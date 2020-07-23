from urllib.parse import urlparse, urlencode
from base64 import b64encode, b64decode
import requests
import datetime


class Query:

    def __init__(self, fields, startDate=datetime.date.today().isoformat(), \
            filterExp=""):
        self.queryfields = self.QueryFields(fields, startDate)
        self.filterExp = self.filter_prepare(expression=filterExp)

    def prepare(self):
        """ Format a query in str for use in url. """

        query = '{}"fields":{}'.format('{', self.queryfields.prepare())

        if self.filterExp:
            query += f',"filterExp":"{self.filterExp}"'

        query += '}'
        return query

    def filter_prepare(self, expression=""):
        return expression.replace('"', "'")

    class QueryFields:
        def __init__(self, names, startDate=datetime.date.today().isoformat()):
            self.names = names
            self.startDate = startDate

        def prepare(self):
            """ Format a query in str for use in url. """

            fields = []
            for field in self.names:
                fields.append({
                    "name": field,
                    "startDate": self.startDate
                })

            return str(fields).replace("'", '"').replace(" ", "")


class Client:

    def __init__(self, url: str, username: str, pwd: str, *args, **kwargs):
        """ Create a conection with nettime app using recived parameters. """

        super().__init__(*args, **kwargs)
        self.nettime_url = urlparse(url)
        self.username = username
        self.pwd = b64encode(pwd.encode('utf-8'))

        ### None values
        self.access_token = None
        self.headers = None
        self.user_rol = None

        #connect client automatically
        self.connect()

    def __str__(self):
        return '{}{} en {}'.format(
            f'{self.access_token} para ' if self.access_token else '',
            self.username,
            self.nettime_url.geturl()
        )

    def __repr__(self):
        return "{}(url='{}', username='{}', pwd='{}')".format(
            self.__class__.__name__,
            self.nettime_url.geturl(),
            self.username,
            b64decode(self.pwd).decode('utf-8'),
        )

    @property
    def is_connected(self):
        """ Informs if client has headers and access_token. """

        return bool(self.headers) and bool(self.access_token)

    def connect(self):
        """ Connect the client to get access_token and headers values. """

        if self.is_connected:
            return

        url = f'{self.nettime_url.geturl()}/api/login'
        data = {
            "username": self.username,
            "pwd": b64decode(self.pwd).decode('utf-8'),
        }
        response = requests.post(url, data=data)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        json_data = response.json()

        if not json_data.get("ok"):
            raise ConnectionError(json_data.get("message"))

        self.access_token = json_data.get("access_token")
        self.headers = self.get_headers()
        self.settings = self.get_settings()
        self.user_rol = self.get_user_rol()

    def reconnect(self):
        """ Reconnect client cleaning headers and access_token. """

        #clean token and headers for safety
        self.access_token = None
        self.headers = None

        self.connect()

    def get_headers(self):
        """ Return headers for a specific conection """

        if not self.access_token:
            raise ConnectionError("El cliente esta desconectado.")

        return {
            "DNT": "1",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept-Encoding": "gzip,deflate",
            "Cookie": f"sessionID={self.access_token}; i18next=es",
        }

    def disconnect(self):
        """ Disconnect a client to lock the access_token. """

        if not self.is_connected:
            raise ConnectionError("El cliente esta desconectado.")

        url = f'{self.nettime_url.geturl()}/api/logout'
        response = requests.post(url, data="", headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        self.access_token = None
        self.headers = None

    def get_settings(self):
        """ Get settings of netTime Server. """

        if not self.is_connected:
            raise ConnectionError("El cliente esta desconectado.")

        url = f'{self.nettime_url.geturl()}/api/settings'
        response = requests.get(url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_settings()
        
        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

        return response.json()

    def get_user_rol(self):
        """ Get user_rol of current session. """

        if not self.is_connected:
            raise ConnectionError("El cliente esta desconectado.")

        return self.settings.get('rol')

    def get_fields(self, container, filterFields=False):
        """ Get all fields of an specific container. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        # url process
        url = f'{self.nettime_url.geturl()}/api/container/fields'
        lookup = {
            "container": container,
            "filterFields": filterFields
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # consulting nettime
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_fields(container, filterFields)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

        # to json
        json_data = response.json()

        return json_data
    
    def get_elements(self, container, query=Query(["id", "name"]), \
            *args, **kwargs):
        """ Get elements of an specific container for general propose. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        url = f'{self.nettime_url.geturl()}/api/container/elements'
        lookup = {
            "pageStartIndex": 0,
            "pageSize": kwargs.get("pageSize", 50),
            "search": kwargs.get("search", ""),
            "order": kwargs.get("order", ""),
            "desc": kwargs.get("desc", ""),
            "container": container,
            "query": query.prepare()
        }

        lookup_url = f'{url}?{urlencode(lookup)}'
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_elements(container, query, *args, **kwargs)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

        # to json
        json_data = response.json()

        return json_data
        
    def get_employees(self, query=Query(["id", "nif"]), *args, **kwargs):
        """ Get employees from nettime. """

        # use get general propose
        employees = self.get_elements(
            container="Persona", query=query, *args, **kwargs)

        return employees

    def container_action_exec(self, container, action, elements, _all=False, \
            dataObj=None):
        """ Execute an action for a container. """
        
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        # url and data prepare
        url = f'{self.nettime_url.geturl()}/api/container/action/exec'
        json_data = {
            "container": container,
            "action": action,
            "all": _all,
            "elements": elements,
            "dataObj": dataObj
        }

        # response process
        response = requests.post(url, json=json_data, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.container_action_exec(
                container, action, elements, _all, dataObj)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

        return response

    def container_save(self, container, elements, dataObj, _all=False):
        """ Update an element of a container with the received values. """

        # data prepare
        data = {
            "action": "Save",
            "container": container,
            "elements": elements,
            "_all": _all,
            "dataObj": dataObj,
        }

        # executing and processing
        response = self.container_action_exec(**data)

        return response.json()

    def get_for_duplicate(self, container, element, _all=False):
        """ Get form for a new element with data of recived element. """

        # data prepare
        data = {
            "action": "Copy",
            "container": container,
            "elements": [element],
            "_all": _all,
        }

        # executing and processing
        response = self.container_action_exec(**data)

        if not response.json():
            raise ValueError("Error obteniendo el formulario de duplicado.")
        
        # data of response
        obj = response.json()[0]
        return obj.get("dataObj")


    def get_element_def(self, container, elements, _all=False, read_only=False):
        """ Get all properties of an object/s. """

        # data prepare
        data = {
            "container": container,
            "elements": elements,
            "_all": _all,
            "action": "editForm" if not read_only else "View",
        }

        # executing and processing
        response = self.container_action_exec(**data)

        elem_defs = []
        for elem in response.json():
            elem_defs.append(elem.get("dataObj"))

        return elem_defs

    def get_create_form(self, container):
        """ Get default data for a new element. """
        
        # data prepare
        data = {
            "container": container,
            "elements": [-1],
        }

        # execute and process
        response = self.get_element_def(**data)

        if not response:
            raise ValueError("Error obteniendo formulario de creación")

        return response[0]
