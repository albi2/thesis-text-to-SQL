from dataclasses import dataclass
from enum import Enum


class SchemaFormat(Enum):
    M_SCHEMA = "m_schema"
    DDL = "ddl"
    JSON = "json"


class SchemaType(Enum):
    FULL = "full"
    FILTERED_TABLES = "filtered_tables"
    FILTERED_TABLES_AND_COLUMNS = "filtered_tables_and_columns"


@dataclass
class SchemaRepresentation:
    schema: str
    format: SchemaFormat
    type: SchemaType