from cassandra.cluster import Session
from cassandra.query import SimpleStatement
from typing import List, Optional, Dict
from enum import Enum


class Index(Enum):
    SAI = 'StorageAttachedIndex'
    SASI = 'org.apache.cassandra.index.sasi.SASIIndex'


class LexicalSearchSession:

    def __init__(self, session: Session):
        self.session = session
    
    def create_table(self,
                     keyspace: str,
                     table_name: str,
                     fields: Dict[str, str],
                     primary_key: List[str]) -> None:
        self.session.set_keyspace(keyspace)
        fields = ', '.join([' '.join([k, v]) for k, v in fields.items()])
        create_table_statement = SimpleStatement(f"""CREATE TABLE IF NOT EXISTS
                                             {keyspace}.{table_name} ({fields},
                                             PRIMARY KEY ({' ,'.join(primary_key)}));""")
        self.execute(create_table_statement).all()
        print(f"Table {keyspace}.{table_name} created successfully.")

    def create_index(self,
                 keyspace: str,
                 table_name: str,
                 field_name: str,
                 index_name: str,
                 index_type: Optional[Index] = Index.SAI,
                 index_analyzer_options: Optional[str] = None):
        self.session.set_keyspace(keyspace)
        create_index_statement = f"""CREATE CUSTOM INDEX {index_name} ON {keyspace}.{table_name}({field_name}) USING '{index_type.value}'"""
        if index_analyzer_options is not None:
            create_index_statement = ' '.join([create_index_statement, index_analyzer_options])
        create_index_statement = SimpleStatement(''.join([create_index_statement, ';']))
        self.execute(create_index_statement).all()

    def insert_row(self,
                   keyspace: str,
                   table_name: str,
                   *args):
        fields = ', '.join(args)
        values = ', '.join(['%s'*len(args)])
        insert_query = f"""
        INSERT INTO {keyspace}.{table_name} ({fields}) VALUES ({values});"""
        self.execute(insert_query, (args)).all()

    def execute(self, *args):
        return self.session.execute(*args)
