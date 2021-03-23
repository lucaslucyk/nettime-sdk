from urllib.parse import urlparse, urlencode, urljoin, quote
from base64 import b64encode, b64decode
import requests
import datetime
# import re
# import math

__specmanager__ = "5.0.0r17013"

class Client:
    
    def __init__(self, url: str, apikey: str, *args, **kwargs):
        """
        Create a conection with Certronic API using recived parameters.
        """

        self.client_url = urlparse(url)
        self.apikey = b64encode(apikey.encode('utf-8'))

    def __str__(self):
        return f'Client for {self.client_fullpath}'

    def __repr__(self):
        return "{}(url='{}', apikey='{}')".format(
            self.__class__.__name__,
            self.client_url.geturl(),
            b64decode(self.apikey).decode('utf-8'),
        )

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return

    @property
    def client_fullpath(self):
        return urljoin(self.client_url.geturl(), self.client_url.path)

    @property
    def headers(self):
        """ Get headers of the client with current data """

        # empty headers initial
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
            "apikey": b64decode(self.apikey).decode('utf-8')
        }

    def get(self, path: str, params: dict = None, **kwargs):
        """
        Sends a GET request to SPEC Manager url.

        :param path: path to add to URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # query prepare
        query = {
            "url": urljoin(self.client_fullpath, path),
            "params": urlencode(params, quote_via=quote),
            "headers": self.headers,
            "timeout": kwargs.get("timeout", 20),
            "stream": kwargs.get("stream", False)
        }

        # consulting nettime
        response = requests.get(**query)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(f'{response.status_code}: {response.text}')

        # to json -> json
        try:
            # if request is stream type, return all response
            if kwargs.get("stream"):
                return response

            # return json response
            return response.json()
        except:
            return {}

    def post(self, path, params: dict = None, data: dict = None, \
            json: dict = None, **kwargs):
        """
        Sends a POST request to SPEC Manager url.

        :param url: URL for the new :class:`Request` object.
        :param json: (optional) json data to send in the query of the request 
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the 
            :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # query prepare
        query = {
            "url": urljoin(self.client_fullpath, path),
            "params": urlencode(params, quote_via=quote),
            "data": data,
            "json": json,
            "headers": self.headers,
            "timeout": kwargs.get("timeout", 20),
        }

        # consulting nettime
        response = requests.post(**query)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json -> json
        try:
            return response.json()
        except:
            return {}

    def get_clockings(self, _type: str, _from: datetime.datetime, \
            _to: datetime.datetime, fromHistory: bool = False, \
            employeeDetail: bool = False, employeeData: list = [], \
            pageSize: int = 20, page: int = 1, **kwargs):
        """
        Get clockings from SM API with self.get() passing _type and 
        parameters recived.

        :param _type: Employee type. Eg. 'employee', 'contractor', etc.
        :param _from: Datetime to apply as start filter of clockings 
        :param _to: Datetime to apply as end filter of clockings 
        :param fromHistory: True or False to get clockings from HISTORICO
        :param employeeDetail: True to get serialized employee. Code by default
        :param employeeData: List of Optional Data of employee to get from SM
        :param pageSize: Max results per page
        :param page: Page number
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`json` object
        :rtype: json
        """
        
        # path prepare
        path = f'clockings/{_type}'

        # datetime to str
        if isinstance(_from, datetime.datetime):
            _from = _from.strftime("%Y%m%d%H%M%S")

        if isinstance(_to, datetime.datetime):
            _to = _to.strftime("%Y%m%d%H%M%S")

        # parameters prepare
        params = {
            "from": _from,
            "to": _to,
            "fromHistory": fromHistory,
            "employeeDetail": employeeDetail,
            "pageSize": pageSize,
            "page": page
        }

        # append data
        if employeeData:
            params["employeeData"] = ','.join([str(e) for e in employeeData])

        # request.get -> json
        return self.get(path=path, params=params, **kwargs)
        

    def get_clockings_contractor(self, _from: datetime.datetime, \
            _to: datetime.datetime, fromHistory: bool = False, \
            employeeDetail: bool = False, employeeData: list = [], \
            pageSize: int = 20, page: int = 1, **kwargs):
        """
        Get contractor clockings from SM API with self.get_clockings() and 
        recived parameters.

        :param _from: Datetime to apply as start filter of clockings 
        :param _to: Datetime to apply as end filter of clockings 
        :param fromHistory: True or False to get clockings from HISTORICO
        :param employeeDetail: True to get serialized employee. Code by default
        :param employeeData: List of Optional Data of employee to get from SM
        :param pageSize: Max results per page
        :param page: Page number
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`json` object
        :rtype: json
        """

        # parameters prepare
        params = {
            "_type": "contractor",
            "_from": _from,
            "_to": _to,
            "fromHistory": fromHistory,
            "employeeDetail": employeeDetail,
            "pageSize": pageSize,
            "page": page,
            "employeeData": employeeData
        }

        # request.get -> json
        return self.get_clockings(**params, **kwargs)

    def post_employee(self, _type: str, code: int, nif: str, lastName: str, \
            firstName: str, companyCode: str, companyName: str, \
            comment: str = None, centers: list = [], optionalData: list = [], \
            isActive: bool = None, **kwargs):
        """
        Send employee to SM API with self.post() passing _type and 
        recived parameters.

        :param _type: str with employee type (enpoint to add in 
            POST /employees/{_type} SM API). E.g.
            'contractor', 'encae', 'employee', etc
        :param code: int with employee code
        :param nif: str with employee DNI field
        :param ss: str with employee SS field
        :param lastName: str with employee lastName field
        :param firstName: str with employee firstName field
        :param companyCode: str with company code (nif)
        :param companyName: str with company name
        :param comment: str with comment to assign at current employee
        :param centers: list of dict with 'center' and 'dueDate' keys. E.g.
            [{
                "center": "AR",
                "dueDate": datetime.date(2020, 12, 31)
            }, {
                "center": "ES",
                "dueDate": datetime.date(2021, 12, 31)
            }]
        :param optionalData: list of dict with opcionals data to assign. E.g.
            [{
                "level": 1,
                "value": "some-value-to-data-1",
            },{
                "level": 8,
                "value": "some-value-to-data-8",
            }]
        :param isActive: boolean to high/down employee
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`json` object
        :rtype: json
        """

        # path prepare
        path = f'employees/{_type}'

        # json prepare
        params = {
            "code": code,
            "nif": nif,
            "lastName": lastName,
            "firstName": firstName,
            "comment": comment,
            "isActive": isActive,
            "companyCode": companyCode,
            "companyName": companyName,
        }

        # centers parse
        if centers:
            params["centers"] = ','.join([
                f'{_c.get("center")}:{_c.get("dueDate").strftime("%Y%m%d")}' \
                    for _c in centers
            ])

        if optionalData:
            params["optionalData"] = ','.join([
                f'{_od.get("level")}:{_od.get("value")}'for _od in optionalData
            ])

        # request.get -> json
        return self.post(path=path, params=params, **kwargs)

    def post_employees(self, employeeData, **kwargs):
        """
        Send employee to SM API with self.post_employee() passing employeeData.

        :param employeeData: Dict or list with params of self.post_employee()
            To get more info of employeeData structure, check help for 
            post_employee() method
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`json` object
        :rtype: json
        """

        # check items
        if isinstance(employeeData, list):
            # empty response
            response = {}
            
            for employee in employeeData:
                # rewrite if OK, raise if error
                response = self.post_employee(**employee, **kwargs)

            # return last response (or raise before)
            return response

        # 1 dict employee by default
        return self.post_employee(**employeeData, **kwargs)

    def post_employee_encae(self, code: int, nif: str, \
            lastName: str, firstName: str, companyCode: str, \
            companyName: str, centers: list = [], optionalData: list = [], \
            **kwargs):
        """
        -- DONT USE
        Send encae employee to SM API with self.post_employee() and 
        recived parameters.

        :param code: int with employee code
        :param nif: str with employee DNI field
        :param ss: str with employee SS field
        :param lastName: str with employee lastName field
        :param firstName: str with employee firstName field
        :param companyCode: str with company code (nif)
        :param companyName: str with company name
        :param centers: list of dict with 'center' and 'dueDate' keys. E.g.
            [{
                "center": "AR",
                "dueDate": datetime.date(2020, 12, 31)
            }, {
                "center": "ES",
                "dueDate": datetime.date(2021, 12, 31)
            }]
        :param optionalData: list of dict with opcionals data to assign. E.g.
            [{
                "level": 1,
                "value": "some-value-to-data-1",
            },{
                "level": 8,
                "value": "some-value-to-data-8",
            }]
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`json` object
        :rtype: json
        """

        # json prepare
        query = {
            "_type": "encae",
            "code": code,
            "nif": nif,
            "lastName": lastName,
            "firstName": firstName,
            "companyCode": companyCode,
            "companyName": companyName,
            "centers": centers,
            "optionalData": optionalData
        }

        # request.get -> json
        return self.post_employee(**query, **kwargs)

