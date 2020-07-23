# nettime-sdk
sdk for netTime (SPEC, SA)


### Import module

```python
import nettime6 as nt6
```


### Client settings

```python
URL = 'http://NETTIME_SERVER:PORT'
USERNAME = 'YOUR_USERNAME'
PWD = 'YOUR_PASSWORD'
```

### Create a client

```python
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
incidencias = []
for incidencia in client.get_elements("Incidencia").get('items'):
    incidencias.append({"id": incidencia.get("id")})
    
data = {
    "container": "Persona",
    "elements": [8],
    "dataObj": {
        "TimeTypesEmployee": incidencias
    }
}

client.container_save(**data)
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
# edit and then use client.container_save() method
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


### Disconnect

```python
client.disconnect()
client.is_connected
```

    False