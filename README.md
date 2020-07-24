# nettime-sdk
sdk for netTime (SPEC, SA)

### Add src folder to path


```python
import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', 'src'))
```

### Import module


```python
import nettime6 as nt6
from importlib import reload
```

### Client settings


```python
URL = 'http://172.18.4.57:6091'
USERNAME = 'Argentina'
PWD = 'Spec@1234'
```

### Create a client


```python
reload(nt6) # for reaload changes only
client = nt6.Client(url=URL, username=USERNAME, pwd=PWD)
client.is_connected
```




    True



### Get employees with summary method


```python
client.get_employees()
```




    {'total': 1, 'items': [{'id': 8, 'nif': '12345678'}]}



### Filter in response (frontend)


```python
client.get_employees(search="1234")
```




    {'total': 1, 'items': [{'id': 8, 'nif': '12345678'}]}



### Specify fields


```python
query = nt6.Query(fields=["nif", "Apellidos_Nombre", "Province", "birthdate"])
client.get_employees(query=query)
```




    {'total': 1,
     'items': [{'nif': '12345678',
       'Apellidos_Nombre': 'Spec, Argentina',
       'Province': 'CABA',
       'birthdate': '1980-01-04T00:00:00.0000000+01:00'}]}



### Filter in backend with nettime filter


```python
query = nt6.Query(
    fields=["nif", "Apellidos_Nombre", "Province", "birthdate"],
    filterExp='Contains(this.nif, "12345678")'
)
client.get_employees(query=query)
```




    {'total': 1,
     'items': [{'nif': '12345678',
       'Apellidos_Nombre': 'Spec, Argentina',
       'Province': 'CABA',
       'birthdate': '1980-01-04T00:00:00.0000000+01:00'}]}



### Fields definition


```python
fields = client.get_fields("Persona")
print('Total:', fields.get('total'))
fields.get('items')[:2]
```

    Total: 416
    




    [{'id': 30,
      'name': 'id',
      'displayName': 'Id',
      'expr': 'this.id',
      'type': 'int',
      'align': 2,
      'sortable': False,
      'width': 0,
      'group': '',
      'numTempOperators': 0},
     {'id': 31,
      'name': 'name',
      'displayName': 'Clave',
      'expr': 'this.name',
      'type': 'String',
      'align': 2,
      'sortable': True,
      'width': 20,
      'group': 'Datos personales',
      'numTempOperators': 0}]



### Fields definition filtering Properties only


```python
fields_filter = client.get_fields("Persona", filterFields=True)
print('Total:', fields_filter.get('total'))
fields_filter.get('items')[:2]
```

    Total: 409
    




    [{'id': 30,
      'name': 'id',
      'displayName': 'Id',
      'expr': 'this.id',
      'type': 'int',
      'align': 2,
      'sortable': False,
      'width': 0,
      'group': '',
      'numTempOperators': 0},
     {'id': 31,
      'name': 'name',
      'displayName': 'Clave',
      'expr': 'this.name',
      'type': 'String',
      'align': 2,
      'sortable': True,
      'width': 20,
      'group': 'Datos personales',
      'numTempOperators': 0}]



### Get incidencias, and update employee


```python
nt_incidencias = client.get_elements("Incidencia").get('items')
nt_incidencias[:10]
```




    [{'id': 0, 'name': 'Sin incidencia'},
     {'id': 1, 'name': 'Inc. horas extra'},
     {'id': 2, 'name': 'Asuntos propios'},
     {'id': 3, 'name': 'Vacaciones'},
     {'id': 4, 'name': 'Lactancia 30 minutos'},
     {'id': 5, 'name': 'Lactancia 1 hora'},
     {'id': 6, 'name': 'Visita al médico'},
     {'id': 7, 'name': 'Horas sindicales'},
     {'id': 8, 'name': 'Accidente laboral'},
     {'id': 9, 'name': 'Enfermedad'}]




```python
incidencias = []
for incidencia in nt_incidencias:
    incidencias.append({"id": incidencia.get("id")})
    
data = {
    "container": "Persona",
    "elements": [8],
    "dataObj": {
        "TimeTypesEmployee": incidencias
    }
}

client.save_element(**data)
```

##### To add periods, use the key "validity" with a list of elements like:
```python
{
    "id": incidencia.get("id"),
    "validity": [{
        "end": "2040-12-31T00:00:00-03:00",
        "start": "2004-01-01T00:00:00-03:00",
    }]
}
```

### Get elements definition


```python
employee = client.get_element_def(container="Persona", elements=[8])
employee = employee[0]

# show calendars
employee.get('Calendar')
```




    {'id': 8,
     '_c_': '',
     'created': '0001-01-01T00:00:00.0000000',
     'modified': '0001-01-01T00:00:00.0000000',
     'name': '8',
     'rev': 0,
     'years': [{'Year': 2020, 'days': {}},
      {'Year': 2021, 'days': {}},
      {'Year': 2019, 'days': {}}],
     'Cycles': [],
     'Calendars': [{'id': 2,
       'name': 'calendar1',
       'Validity': [{'start': '2020-01-01T00:00:00.0000000',
         'end': '2020-06-30T00:00:00.0000000'}]},
      {'id': 5, 'name': 'ARG'}],
     'nodesSource': [],
     'multiName': {'es-ES': '8'}}



### Get default values in create form


```python
client.get_create_form("Jornada")
```




    {'_c_': 'Jornada',
     'id': -1,
     'modified': '0001-01-01T00:00:00.0000000',
     'created': '0001-01-01T00:00:00.0000000',
     'color': '808080',
     'rev': 0,
     'minutosCortesia': 0,
     'minutosPenalizacion': 0,
     'totalTeorico': 480,
     'minutoFinal': 2880,
     'minutosRetraso': 0,
     'resultados': [],
     'multiName': {},
     'nodesSource': [],
     'incidencias': [],
     'baObligada': [],
     'baFlexible': [],
     'pausas': [],
     'intervalSource': [{'data': 'flex', 'label': 'Bloque flexible'},
      {'data': 'oblig', 'label': 'Bloque obligatorio'},
      {'data': 'all', 'label': 'Toda la jornada'},
      {'data': 'bloque', 'label': 'Bloque del grupo de incidencia'},
      {'data': 'relative', 'label': 'Relativo a...', 'state': 'relative'},
      {'data': 'delete', 'label': 'Sin validez'}],
     'ShifttimeTypesMassIdinci': [],
     'relativeSource': [{'data': 'inishift', 'label': 'Inicio de la jornada'},
      {'data': 'firstflexmin', 'label': 'Inicio bloque flexible'},
      {'data': 'firstoblmin', 'label': 'Inicio bloque obligatorio'},
      {'data': 'endshift', 'label': 'Final de la jornada'},
      {'data': 'endflex', 'label': 'Final bloque flexible'},
      {'data': 'endobli', 'label': 'Final bloque obligatorio'}]}



### Get dataObj for duplicate element


```python
client.get_for_duplicate(container="Arbol", element=9)
# edit and then use client.save_element() method
```




    {'_c_': 'Arbol',
     'id': -1,
     'name': 'ARGENTINA',
     'rev': 0,
     'createdBy': 'Admin',
     'created': '2020-06-29T09:37:18.7470000',
     'modified': '0001-01-01T00:00:00.0000000',
     'color': '7D7D7D',
     'allowedContainerNames': 'Empleados',
     'order': 0,
     'internalName': 'ARGENTINA',
     'idNodeParent': 1,
     'baAllowedContainers': [14],
     'nodesSource': [],
     'nodes': [],
     'multiName': {'es-ES': 'ARGENTINA'}}



### Delete element


```python
client.get_elements("Jornada", search="TEST")
```




    {'total': 1, 'items': [{'id': 28, 'name': 'TEST DELETE'}]}




```python
client.delete_element(container="Jornada", elements=[28])
```




    [{'type': 8,
      'id': 'HQAAAAOAAAEACASAAA==',
      'rev': 75,
      'message': 'Los elementos se han eliminado correctamente.'}]




```python
client.get_elements("Jornada", search="TEST")
```




    {'total': 0, 'items': []}



### Getting day results info


```python
client.get_day_info(employee=8, _from="2020-07-03", to="2020-07-03")
```




    {'idEmp': 8,
     'days': [{'date': '2020-07-03T00:00:00.0000000',
       'shift': {'date': '2020-07-03T00:00:00.0000000',
        'idEmp': 8,
        'shift': 20,
        'minFin': 2880,
        'minFinForced': False,
        'shiftPetition': {'actions': ['Change']},
        'clockings': [{'id': 21,
          'date': '2020-07-03T09:00:00.0000000',
          'idElem': 0,
          'type': 'timetypes',
          'idReader': 0,
          'user': 'Argentina',
          'ip': '172.18.4.24',
          'status': {'effective': True,
           'desc': 'Entrando',
           'state': '',
           'entering': True,
           'actions': ['Delete', 'Edit', 'Comment']},
          'app': True,
          'numDocuments': 0},
         {'id': 22,
          'date': '2020-07-03T18:00:00.0000000',
          'idElem': 0,
          'type': 'timetypes',
          'idReader': 0,
          'user': 'Argentina',
          'ip': '172.18.4.24',
          'status': {'effective': True,
           'desc': 'Saliendo',
           'state': '',
           'entering': False,
           'actions': ['Delete', 'Edit', 'Comment']},
          'app': True,
          'numDocuments': 0}],
        'info': {'Change': 'Cambiar',
         'Delete': 'Eliminar',
         'Edit': 'Editar',
         'Comment': 'Comentar'}},
       'results': {'date': '2020-07-03T00:00:00.0000000',
        'hasComments': False,
        'hasPending': False,
        'shift': {'id': 20, 'minutes': {'start': 1980, 'end': 2880}},
        'minutesTypes': [{'name': 'Incidencia',
          'results': [{'id': 0, 'minutes': [{'start': 1980, 'end': 2520}]}]}]}}],
     'taskConfig': 71,
     'info': [{'id': 0,
       'type': 'Incidencia',
       'name': 'Sin incidencia',
       'color': '009933'},
      {'id': 20, 'type': 'Jornada', 'name': 'ARG 09 a18', 'color': '808080'}]}



### Get day results


```python
client.get_results(employee=8, _from="2020-07-03", to="2020-07-03")
```




    {'results': [{'date': '2020-07-03T00:00:00.0000000',
       'hasComments': False,
       'hasPending': False,
       'shift': {'id': 20, 'minutes': {'start': 1980, 'end': 2880}},
       'minutesTypes': [{'name': 'Lector',
         'results': [{'id': -1,
           'values': [{'name': 'Min', 'value': 540},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]}]},
        {'name': 'Incidencia',
         'results': [{'id': 0,
           'values': [{'name': 'Min', 'value': 540},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]}]},
        {'name': 'Sistema',
         'results': [{'id': 0,
           'values': [{'name': 'Min', 'value': 540},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]},
          {'id': 5,
           'values': [{'name': 'Min', 'value': 0},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 0},
            {'name': 'EvtDes', 'value': 0}]},
          {'id': 6,
           'values': [{'name': 'Min', 'value': 540},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]},
          {'id': 8,
           'values': [{'name': 'Min', 'value': 480},
            {'name': 'MinDes', 'value': 60},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 1}]},
          {'id': 10,
           'values': [{'name': 'Min', 'value': 0},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 0},
            {'name': 'EvtDes', 'value': 0}]},
          {'id': 11,
           'values': [{'name': 'Min', 'value': 480},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]},
          {'id': 12,
           'values': [{'name': 'Min', 'value': 540},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]}]},
        {'name': 'Anomalia',
         'results': [{'id': 0,
           'values': [{'name': 'Min', 'value': 0},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]}]},
        {'name': 'Jornada',
         'results': [{'id': 20,
           'values': [{'name': 'Min', 'value': 480},
            {'name': 'MinDes', 'value': 0},
            {'name': 'Evt', 'value': 1},
            {'name': 'EvtDes', 'value': 0}]}]},
        {'name': 'Aritmetico',
         'results': [{'id': 1,
           'values': [{'name': 'Value', 'value': 60},
            {'name': 'Accumulated', 'value': 60},
            {'name': 'Available', 'value': -60},
            {'name': 'Discard', 'value': 0}]},
          {'id': 2,
           'values': [{'name': 'Value', 'value': 60},
            {'name': 'Accumulated', 'value': -900},
            {'name': 'Available', 'value': 900},
            {'name': 'Discard', 'value': 0}]},
          {'id': 3,
           'values': [{'name': 'Value', 'value': 60},
            {'name': 'Accumulated', 'value': -62820},
            {'name': 'Available', 'value': 62820},
            {'name': 'Discard', 'value': 0}]},
          {'id': 4,
           'values': [{'name': 'Value', 'value': 0},
            {'name': 'Accumulated', 'value': 0},
            {'name': 'Available', 'value': 22},
            {'name': 'Discard', 'value': 0}]},
          {'id': 5,
           'values': [{'name': 'Value', 'value': 40},
            {'name': 'Accumulated', 'value': 40},
            {'name': 'Available', 'value': -40},
            {'name': 'Discard', 'value': 0}]},
          {'id': 6,
           'values': [{'name': 'Value', 'value': 0},
            {'name': 'Accumulated', 'value': 0},
            {'name': 'Available', 'value': 22},
            {'name': 'Discard', 'value': 0}]},
          {'id': 7,
           'values': [{'name': 'Value', 'value': 0},
            {'name': 'Accumulated', 'value': 0},
            {'name': 'Available', 'value': 22},
            {'name': 'Discard', 'value': 0}]}]}]}],
     'info': [{'id': -1, 'type': 'Lector', 'name': 'UNKNOWN', 'color': 'FDFDFD'},
      {'id': 0, 'type': 'Incidencia', 'name': 'Sin incidencia', 'color': '009933'},
      {'id': 0,
       'type': 'Sistema',
       'name': 'Productivas en el centro',
       'color': '009933'},
      {'id': 0, 'type': 'Anomalia', 'name': 'Sin anomalía', 'color': 'EEEEEE'},
      {'id': 5,
       'type': 'Sistema',
       'name': 'Ausencias no justificadas',
       'color': 'C83327'},
      {'id': 6, 'type': 'Sistema', 'name': 'Productivas', 'color': '3399FF'},
      {'id': 8, 'type': 'Sistema', 'name': 'Trabajadas', 'color': '009933'},
      {'id': 10, 'type': 'Sistema', 'name': 'Retrasos', 'color': 'CC6600'},
      {'id': 11, 'type': 'Sistema', 'name': 'Jornada teórica', 'color': 'FFFFFF'},
      {'id': 12, 'type': 'Sistema', 'name': 'Filtro día', 'color': 'FFFFFF'},
      {'id': 20, 'type': 'Jornada', 'name': 'ARG 09 a18', 'color': '808080'},
      {'id': 1, 'type': 'Aritmetico', 'name': 'Saldo diario', 'color': '0066CC'},
      {'id': 2, 'type': 'Aritmetico', 'name': 'Saldo mensual', 'color': 'CC9900'},
      {'id': 3, 'type': 'Aritmetico', 'name': 'Saldo anual', 'color': 'FF6600'},
      {'id': 4,
       'type': 'Aritmetico',
       'name': 'Saldo Días Vacaciones',
       'color': '007373',
       'numeric': True},
      {'id': 5,
       'type': 'Aritmetico',
       'name': 'edad',
       'color': '3ef7a4',
       'numeric': True},
      {'id': 6,
       'type': 'Aritmetico',
       'name': 'TEST VACACIONES',
       'color': '007373',
       'numeric': True},
      {'id': 7,
       'type': 'Aritmetico',
       'name': 'Saldo Días Vacaciones 3',
       'color': '0000ff',
       'numeric': True}]}



### Add clocking


```python
client.add_clocking(employee=8, date="2020-07-02", time="18:30")
```




    {'ok': True}



### Get day clockings


```python
client.get_day_clockings(employee=8, date="2020-07-02")
```




    {'date': '2020-07-02T00:00:00.0000000',
     'idEmp': 8,
     'shift': 20,
     'minFin': 0,
     'minFinForced': False,
     'shiftPetition': {'actions': ['Change']},
     'clockings': [{'id': 85,
       'date': '2020-07-02T15:00:00.0000000',
       'idElem': 0,
       'type': 'timetypes',
       'idReader': 0,
       'user': 'Argentina',
       'ip': '172.18.4.24',
       'status': {'effective': True,
        'desc': 'Entrando',
        'state': '',
        'entering': True,
        'actions': ['Delete', 'Edit', 'Comment']},
       'app': True,
       'numDocuments': 0},
      {'id': 89,
       'date': '2020-07-02T18:30:00.0000000',
       'idElem': 0,
       'type': 'timetypes',
       'idReader': 0,
       'user': 'Argentina',
       'ip': '172.18.4.24',
       'status': {'effective': True,
        'desc': 'Saliendo',
        'state': '',
        'entering': False,
        'actions': ['Delete', 'Edit', 'Comment']},
       'app': True,
       'numDocuments': 0}],
     'info': {'Change': 'Cambiar',
      'Delete': 'Eliminar',
      'Edit': 'Editar',
      'Comment': 'Comentar'}}



### Edit clocking


```python
client.edit_clocking(employee=8, clocking_id=89, date="2020-07-02", time="20:30")
```




    {'ok': True}



### Delete clocking


```python
client.delete_clocking(employee=8, clocking_id=89, date="2020-07-02", time="18:30")
```




    {'ok': True}



### Plannings


```python
planning = client.get_create_form("Persona", action="NewPlanificacion")
planning.update({
    "name": "Testing Planning",
    "allDay": True,
    "allDayId": 9, #Timetype ID
    "employee": [8], #Employee ID
    "dateInterval": client.get_days_offset(["2020-10-10", "2020-10-11"]),
})
# dateInterval is a list of int with differences between setting firstDate
# can use get_days_offset() method
```


```python
data = {
    "container": "IncidenciaFutura",
    "dataObj": planning,
}
client.save_element(**data)
```




    [{'type': 6,
      'dataObject': {'id': 6,
       '_c_': 'IncidenciaFutura',
       'firstDay': '2020-10-10T00:00:00.0000000',
       'rev': 54,
       'modifiedBy': 'Argentina',
       'modified': '2020-07-24T21:14:09.2941556+02:00',
       'createdBy': 'Argentina',
       'created': '2020-07-24T21:14:09.2631547+02:00',
       'allDayId': 9,
       'allDay': True,
       'selfOwner': False,
       'state': '0',
       'name': 'Testing Planning',
       'comments': '',
       'intState': 0,
       'isAccepted': True,
       'lastDay': '2020-10-11T00:00:00.0000000',
       'numDays': 2,
       'confirmBy': 'Argentina',
       'confirm': '2020-07-24T21:14:09.2781687+02:00',
       'describe': '2 días, del 10/10/2020 al 11/10/2020 Todo el día con incidencia Enfermedad',
       'hasComment': False,
       'error': '',
       'stateDescription': 'Aceptada',
       'describeTT': 'Enfermedad',
       'isPending': False,
       'isValidationPending': False,
       'isDenied': False,
       'totalDocs': 0,
       'validatedDays': [],
       'dateInterval': [6127, 6128],
       'baValidElems': [1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24],
       'timeTypes': [9],
       'nodesSource': [],
       'employee': 8},
      'message': 'El elemento se ha creado correctamente.',
      'showActions': True}]



### Add planning with summary method


```python
# Delete last added element
client.delete_element(container="IncidenciaFutura", elements=[6])
```




    [{'type': 8,
      'id': 'BwAAAAEAAgeAAA==',
      'rev': 57,
      'message': 'Realizada la solicitud de eliminación.'}]




```python
client.add_planning(
    employee=8,
    name="Testing summary planning",
    timetype=9,
    days=["2020-10-10", "2020-10-11"],
)
```




    [{'type': 6,
      'dataObject': {'id': 7,
       '_c_': 'IncidenciaFutura',
       'firstDay': '2020-10-10T00:00:00.0000000',
       'rev': 60,
       'modifiedBy': 'Argentina',
       'modified': '2020-07-24T21:40:11.0364860+02:00',
       'createdBy': 'Argentina',
       'created': '2020-07-24T21:40:10.9753242+02:00',
       'allDayId': 9,
       'allDay': True,
       'selfOwner': False,
       'state': '0',
       'name': 'Testing summary planning',
       'comments': '',
       'intState': 0,
       'isAccepted': True,
       'lastDay': '2020-10-11T00:00:00.0000000',
       'numDays': 2,
       'confirmBy': 'Argentina',
       'confirm': '2020-07-24T21:40:11.0063244+02:00',
       'describe': '2 días, del 10/10/2020 al 11/10/2020 Todo el día con incidencia Enfermedad',
       'hasComment': False,
       'error': '',
       'stateDescription': 'Aceptada',
       'describeTT': 'Enfermedad',
       'isPending': False,
       'isValidationPending': False,
       'isDenied': False,
       'totalDocs': 0,
       'validatedDays': [],
       'dateInterval': [6127, 6128],
       'baValidElems': [1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24],
       'timeTypes': [9],
       'nodesSource': [],
       'employee': 8},
      'message': 'El elemento se ha creado correctamente.',
      'showActions': True}]



### Edit planning


```python
# search planning
planning_query = nt6.Query(
    fields=["id", "name", "allDayId", ],
    filterExp="((this.employee.nif = '12345678') && (this.firstDay = '2020-10-10'))"
)
client.get_elements(container="IncidenciaFutura", query=planning_query)
```




    {'total': 1,
     'items': [{'id': 7, 'name': 'Testing summary planning', 'allDayId': 9}]}




```python
edit_planning = client.get_element_def(container="IncidenciaFutura", elements=[7])
edit_planning = edit_planning[0]
edit_planning["dateInterval"]
```




    [6127, 6128]




```python
# ever fix employe; must be a list
edit_planning["employee"] = [edit_planning.get("employee")]

# apply your changes
day_to_add = client.get_days_offset(["2020-10-12"])
edit_planning["dateInterval"].extend(day_to_add)
edit_planning["dateInterval"]
```




    [6127, 6128, 6129]




```python
response = client.save_element(
    container="IncidenciaFutura",
    elements=[7],
    dataObj=edit_planning
)
response[0].get('message')
```




    'El elemento se ha modificado correctamente.'



### Disconnect


```python
client.disconnect()
client.is_connected
```




    False
