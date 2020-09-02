import pandas as pd
import sqlalchemy
from sqlalchemy.pool import NullPool

class Client:

    def __init__(self, username: str, pwd: str, server: str, database: str, \
            port: int = 1433, driver: str = "mssql+pyodbc", \
            controller: str = "SQL Server"):

        self.engine_params = sqlalchemy.engine.url.URL(
            drivername=driver,
            username=username,
            password=pwd,
            host=server,
            port=port,
            database=database,
            query={'driver': controller}
        )

        self.engine = sqlalchemy.create_engine(
            self.engine_params,
            poolclass=NullPool
        )

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self.dispose()


    def dispose(self):
        return self.engine.dispose()

    @property
    def table_names(self):
        return self.engine.table_names()

    def read_sql_query(self, query: str, to_records: bool = False):
        """ Execute query with active engine and return pandas dataframe. """

        # query execute
        df = pd.read_sql_query(query, self.engine)

        if to_records:
            # return json format
            return df.to_dict('records')

        return df

    def insert_values(self, df: pd.DataFrame, table: str, schema: str = None, \
            if_exists: str = 'append', index: bool = False, \
            index_label: str = None, chunksize: int = None, \
            method: str = 'multi', from_records: bool = False):
        
        if from_records:
            # create pandas dataframe
            df = pd.DataFrame.from_records(df)

        # to sql
        df.to_sql(
            name=table,
            schema=schema,
            if_exists=if_exists,
            index=index,
            index_label=index_label,
            chunksize=chunksize,
            method=method    
        )

        return True

    def get_from_table(self, table: str, fields: list = ['*'], \
            top: int = 5, where: str = None, group_by: list = [], **kwargs):
        """ Create and execute a query for get results from Database. """

        # create query
        query = 'SELECT {}{} FROM {}{}{}'.format(
            f'TOP {top}' if top else '',
            ', '.join(fields),
            table,
            f' WHERE {where}' if where else '',
            f' GROUP BY {group_by}' if group_by else ''
        )

        # return results
        return self.read_sql_query(query=query, **kwargs)

    def get_employees(self, **kwargs):
        """ Get employees from database. """

        return self.get_from_table(table="PERSONAS", **kwargs)

