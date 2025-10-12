from typing import Any, Dict, List, Optional
from util.db.database_descriptor import DatabaseDescriptor


class DDLSchemaGenerator:
    def __init__(self, db_id: str = 'Anonymous', schema: Optional[str] = None, database_descriptor: Optional[DatabaseDescriptor] = None, dialect: str = ''):
        self.db_id = db_id
        self.schema = schema
        self.tables = {}
        self.foreign_keys = []
        self.database_descriptor = database_descriptor
        self.dialect = dialect

    def add_table(self, name, fields={}, comment=None):
        self.tables[name] = {"fields": fields.copy(), 'examples': [], 'comment': comment}

    def set_database_descriptor(self, database_descriptor: DatabaseDescriptor):
        self.database_descriptor = database_descriptor

    def add_field(self, table_name: str, field_name: str, field_type: str = "",
            primary_key: bool = False, nullable: bool = True, default: Any = None,
            autoincrement: bool = False, comment: str = "", examples: list = [], **kwargs):
        self.tables[table_name]["fields"][field_name] = {
            "type": field_type,
            "primary_key": primary_key,
            "nullable": nullable,
            "default": default if default is None else f'{default}',
            "autoincrement": autoincrement,
            "comment": comment,
            "examples": examples.copy(),
            **kwargs}

    def add_foreign_key(self, table_name, field_name, ref_schema, ref_table_name, ref_field_name):
        self.foreign_keys.append([table_name, field_name, ref_schema, ref_table_name, ref_field_name])

    def to_ddl(self, selected_tables: List = None, selected_columns: List = None, dialect: str = None) -> str:
        if dialect is None:
            dialect = self.dialect
        output = []

        if selected_tables is not None:
            selected_tables = [s.lower() for s in selected_tables]
        if selected_columns is not None:
            selected_columns = [s.lower() for s in selected_columns]
            if selected_tables is None:
                selected_tables = [s.split('.')[0].lower() for s in selected_columns]

        for table_name, table_info in self.tables.items():
            if selected_tables is None or table_name.lower() in selected_tables:
                output.append(f"CREATE TABLE {table_name} (")
                
                field_lines = []
                primary_keys = []
                
                for field_name, field_info in table_info['fields'].items():
                    if selected_columns is not None and f"{table_name}.{field_name}".lower() not in selected_columns:
                        continue

                    field_line = f"    {field_name} {field_info['type']}"
                    if field_info.get('primary_key', False):
                        primary_keys.append(field_name)
                    if field_info.get('autoincrement', False):
                        if dialect == 'sqlite':
                            # SQLite uses AUTOINCREMENT on the PRIMARY KEY for INTEGER columns
                            pass
                        elif dialect == 'postgresql':
                            field_line = f"    {field_name} SERIAL"
                        elif dialect == 'mysql':
                            field_line += " AUTO_INCREMENT"
                        elif dialect == 'mssql':
                            field_line += " IDENTITY(1,1)"
                    if not field_info.get('nullable', True):
                        field_line += " NOT NULL"
                    if field_info.get('unique', False):
                        field_line += " UNIQUE"
                    if field_info.get('default') is not None:
                        field_line += f" DEFAULT {field_info['default']}"
                    
                    comment = field_info.get('comment', '')
                    if not comment and self.database_descriptor:
                        table_descriptor = self.database_descriptor.tables.get(table_name)
                        if table_descriptor:
                            column_definition = table_descriptor.columns.get(field_name)
                            if column_definition:
                                if column_definition.column_description:
                                    comment += f"Column Description: {column_definition.column_description}"
                                if column_definition.value_description:
                                    comment += f", Column Value Explanation: {column_definition.value_description}"
                    if comment:
                        field_line += f" -- {comment.strip()}"

                    field_lines.append(field_line)

                if primary_keys:
                    field_lines.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")

                for fk in self.foreign_keys:
                    table1, column1, _, table2, column2 = fk
                    if table1.lower() == table_name.lower():
                         if selected_tables is None or \
                            (table1.lower() in selected_tables and table2.lower() in selected_tables):
                            field_lines.append(f"    CONSTRAINT fk_{table1}_{column1} FOREIGN KEY ({column1}) REFERENCES {table2} ({column2})")

                output.append(',\n'.join(field_lines))
                output.append(");")

        return '\n\n'.join(output)