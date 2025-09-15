from dataclasses import dataclass, field
from typing import Dict

from dataclasses import asdict

@dataclass
class ColumnDefinition:
    original_column_name: str = ""
    column_name: str = ""
    column_description: str = ""
    data_format: str = ""
    value_description: str = ""

    def to_dict(self):
        return asdict(self)

@dataclass
class TableDescriptor:
    table_name: str
    columns: Dict[str, ColumnDefinition] = field(default_factory=dict)

    def to_dict(self):
        return {
            "table_name": self.table_name,
            "columns": {k: v.to_dict() for k, v in self.columns.items()}
        }

@dataclass
class DatabaseDescriptor:
    db_id: str
    tables: Dict[str, TableDescriptor] = field(default_factory=dict)

    def to_dict(self):
        return {
            "db_id": self.db_id,
            "tables": {k: v.to_dict() for k, v in self.tables.items()}
        }

    @staticmethod
    def from_dictionary(db_id: str, db_dictionary: Dict[str, Dict[str, Dict[str, str]]]) -> 'DatabaseDescriptor':
        db_descriptor = DatabaseDescriptor(db_id=db_id)
        for table_name, table_data in db_dictionary.items():
            columns = {
                col_name: ColumnDefinition(**col_data)
                for col_name, col_data in table_data.items()
            }
            db_descriptor.tables[table_name] = TableDescriptor(table_name=table_name, columns=columns)
        return db_descriptor