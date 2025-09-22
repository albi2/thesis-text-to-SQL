from dataclasses import dataclass
from enum import Enum

# Make the enum also inherit from 'str'
class SchemaFormat(str, Enum):
    M_SCHEMA = "m_schema"
    DDL = "ddl"
    JSON = "json"

# Make the enum also inherit from 'str'
class SchemaType(str, Enum):
    FULL = "full"
    FILTERED_TABLES = "filtered_tables"
    FILTERED_TABLES_AND_COLUMNS = "filtered_tables_and_columns"


@dataclass
class SchemaRepresentation:
    schema: str
    format: SchemaFormat
    type: SchemaType

    def to_dict(self):
        return {
            "format": str(self.format),
            "type": str(self.type)
        }

    def to_full_dict(self):
        return {
            "schema": self.schema,
            "format": str(self.format),
            "type": str(self.type)
        }