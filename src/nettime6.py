from urllib.parse import urlparse, urlencode
from base64 import b64encode, b64decode
import requests
import datetime


class Query:

    def __init__(self, fields: list, \
            startDate: str=datetime.date.today().isoformat(), \
            filterExp: str=""):
        self.queryfields = self.QueryFields(fields, startDate)
        self.filterExp = self.filter_prepare(expression=filterExp)

    def prepare(self):
        """ Format a query in str for use in url. """

        query = '{}"fields":{}'.format('{', self.queryfields.prepare())

        if self.filterExp:
            query += f',"filterExp":"{self.filterExp}"'

        query += '}'
        return query

    def filter_prepare(self, expression: str=""):
        return expression.replace('"', "'")

    class QueryFields:
        def __init__(self, names: list, \
                startDate: str=datetime.date.today().isoformat()):
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

        if response.status_code not in range(200, 300):
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

        if response.status_code not in range(200, 300):
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
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        return response.json()

    def get_user_rol(self):
        """ Get user_rol of current session. """

        if not self.is_connected:
            raise ConnectionError("El cliente esta desconectado.")

        return self.settings.get('rol')

    def get_days_offset(self, days: list):
        """ 
        Convert a list of datetime.date or str format to int offset with \
        self.setting.firstDate.
        """

        firstYear = self.settings.get('firstDate', None)
        if not firstYear:
            raise RuntimeError("No se puede obtener el setting firstDate.")
        
        # set first_date
        first_date = datetime.date(firstYear, 1, 1)

        # process dates
        days_numbers = []
        for day in days:
            # ensure datetime.date type
            if not isinstance(day, datetime.date):
                day = datetime.date.fromisoformat(day)

            delta = day - first_date
            days_numbers.append(delta.days)

        return days_numbers

    def get_fields(self, container: str, filterFields: bool=False):
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
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        json_data = response.json()

        return json_data
    
    def get_elements(self, container: str, query=Query(["id", "name"]), \
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
        if response.status_code not in range(200, 300):
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

    def container_action_exec(self, container: str, action: str, \
            elements: list, _all: bool=False, dataObj: dict=None, \
            *args, **kwargs):
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
        json_data.update(kwargs)

        # response process
        response = requests.post(url, json=json_data, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.container_action_exec(
                container, action, elements, _all, dataObj)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        return response

    def save_element(self, container: str, dataObj: dict, elements: list=[], \
            _all: bool=False):
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

    def delete_element(self, container: str, elements: list, \
            _confirm: bool=True, _all: bool=False):
        """ Delete an element of a container with the received values. """

        # data prepare
        data = {
            "action": "Delete",
            "container": container,
            "elements": elements,
            "_all": _all,
        }

        # default auto confirm
        if _confirm:
            data["dataObj"] = {
                "_confirm": _confirm,
            }

        # executing and processing
        response = self.container_action_exec(**data)

        return response.json()

    def get_for_duplicate(self, container: str, element: int, _all: bool=False):
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


    def get_element_def(self, container: str, elements: list, \
            _all: bool=False, read_only: bool=False, *args, **kwargs):
        """ Get all properties of an object/s. """

        # data prepare
        data = {
            "container": container,
            "elements": elements,
            "_all": _all,
            "action": "editForm" if not read_only else "View",
        }
        data.update(kwargs)

        # executing and processing
        response = self.container_action_exec(**data)

        elem_defs = []
        for elem in response.json():
            elem_defs.append(elem.get("dataObj"))

        return elem_defs

    def get_create_form(self, container: str, *args, **kwargs):
        """ Get default data for a new element. """
        
        # data prepare
        data = {
            "container": container,
            "elements": [-1],
        }

        # execute and process
        response = self.get_element_def(**data, **kwargs)

        if not response:
            raise ValueError("Error obteniendo formulario de creación")

        return response[0]

    def get_day_info(self, employee: int, \
            _from: str=datetime.date.today().isoformat(), \
            to: str=datetime.date.today().isoformat()):
        """ 
        Get info, days, shifts, and results for a employe in a specific period. 
        """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # url process
        url = f'{self.nettime_url.geturl()}/api/day/results'
        lookup = {
            "idemp": employee,
            "from": _from,
            "to": to
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # consulting nettime
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_day_info(employee, _from, to)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        return response.json()

    def get_access_clockings(self, employee: int, \
            _from: str=datetime.date.today().isoformat(), \
            to: str=datetime.date.today().isoformat()):
        """ Get access clockings for a employe in a specific period. """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # url process
        url = f'{self.nettime_url.geturl()}/api/access/clockings'
        lookup = {
            "idemp": employee,
            "from": _from,
            "to": to
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # consulting nettime
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_access_clockings(employee, _from, to)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        return response.json()

    def get_task_status(self, task):
        """ Get status of an async task. """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # url process
        url = f'{self.nettime_url.geturl()}/api/async/status'
        lookup = {
            "taskid": task
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # get task status
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_task_response(task)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)
        
        # to json
        return response.json()

    def get_task_response(self, task: int):
        """ Return the result of a async task. """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        # ensure the task is complete
        task_status = self.get_task_status(task)
        while not task_status.get("completed", False):
            task_status = self.get_task_status(task)

        # url process
        url = f'{self.nettime_url.geturl()}/api/async/response'
        lookup = {
            "taskid": task,
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # consulting nettime
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_task_response(task)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        return response.json()

    def generate_results_task(self, employee: int, \
            _from: str=datetime.date.today().isoformat(), \
            to: str=datetime.date.today().isoformat()):
        """ Return task id for results of a employee in an specific period. """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        # url process
        url = f'{self.nettime_url.geturl()}/api/results'
        lookup = {
            "idemp": employee,
            "from": _from,
            "to": to
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # consulting nettime
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.generate_results_task(employee, _from, to)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        return response.json()


    def get_results(self, employee: int, \
            _from: str=datetime.date.today().isoformat(), \
            to: str=datetime.date.today().isoformat()):
        """ Get results of day for a employee. """

        # generate async task
        async_tasK_response = self.generate_results_task(employee, _from, to)

        # get task results
        task_results = self.get_task_response(async_tasK_response.get('taskId'))

        # to json
        return task_results

    def clocking_prepare(self, employee: int, date_time: datetime.datetime, \
            reader: int=-1, clocking_id: int=-1, action: str=None):
        """ Return a dict element with recived data. """

        # ensure datetime.datetime type
        if not isinstance(date_time, datetime.datetime):
            date_time = datetime.datetime.fromisoformat(date_time)

        # prepare structure
        clocking_data = {
            "id": clocking_id,
            "action": action,
            "app": True,
            "type": "timetypes",
            "date": date_time.isoformat(timespec='milliseconds'),
            "idReader": reader,
            "idElem": 0,
            "isNew": True if clocking_id == -1 else False,
        }

        return clocking_data
        

    def post_clocking(self, employee: int, date: str, time: str, \
            reader: int=-1, *args, **kwargs):
        """ Add a clocking to a employee in a specific date an time. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        if self.user_rol == 'Persona':
            raise ValueError("Método no soportado para el tipo 'Persona'.")

        #teime process
        if not isinstance(date, datetime.date):
            date = datetime.date.fromisoformat(date)

        if not isinstance(date, datetime.time):
            time = datetime.datetime.strptime(time, "%H:%M").time()

        date_time = datetime.datetime.combine(date, time)

        url = f'{self.nettime_url.geturl()}/api/day/post/'
        json_data = {
            "idEmp": employee,
            "date": date.isoformat(),
            "clockings": [
                self.clocking_prepare(
                    employee=employee,
                    date_time=date_time,
                    reader=reader,
                    action=kwargs.get("action", None),
                    clocking_id=kwargs.get("clocking_id", -1)
                )
            ],
            
        }

        # get response
        response = requests.post(url, json=json_data, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.post_clocking(employee, date, time, reader)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        return response.json()

    def generate_clockings_task(self, employee: int, \
            date: str=datetime.date.today().isoformat()):
        """ Return task id for clockings of a employee in an specific period. """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        # url process
        url = f'{self.nettime_url.geturl()}/api/clockings'
        lookup = {
            "idemp": employee,
            "date": date,
        }
        lookup_url = f'{url}?{urlencode(lookup)}'

        # consulting nettime
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.generate_clockings_task(employee, employee, date)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        return response.json()

    def get_day_clockings(self, employee: int, \
            date: str=datetime.date.today().isoformat()):
        """
        Get all the clockings (Horario) of an employe in a specific day.
        ** This method use portal API.
        """

        # generate async task
        async_tasK = self.generate_clockings_task(employee, date)

        # get task results
        task_results = self.get_task_response(
            async_tasK.get('taskId'))

        # to json
        return task_results

    def add_clocking(self, employee: int, date: str, time: str, \
            reader: int=-1):
        """ Add a clocking using post_clocking() method. """
        
        return self.post_clocking(employee=employee, date=date, time=time)

    def edit_clocking(self, employee: int, clocking_id: int, date: str, \
            time: str):
        """ Delete a clocking using post_clocking() method. """

        return self.post_clocking(
            employee=employee,
            date=date,
            time=time,
            clocking_id=clocking_id
        )

    def delete_clocking(self, employee: int, clocking_id: int, date: str, \
            time: str):
        """ Delete a clocking using post_clocking() method. """
        
        return self.post_clocking(
            employee=employee,
            date=date,
            time=time,
            action="Delete",
            clocking_id=clocking_id
        )

    def add_planning(self, employee: int, name: str, days: list, \
            allDay: bool=True, timetype: int=0):
        """
        Create an absence planning for an employee on the indicated days using \
        the received timetype.
        """

        # getting form and update data
        planning = self.get_create_form("Persona", action="NewPlanificacion")
        planning.update({
            "name": name,
            "allDay": allDay,
            "allDayId": timetype,  # Timetype ID
            "employee": [employee],  # Employee ID
            "dateInterval": self.get_days_offset(days),
        })

        # prepare and save data
        data = {
            "container": "IncidenciaFutura",
            "dataObj": planning,
        }
        return self.save_element(**data)
        