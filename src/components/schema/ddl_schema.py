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
                    # skip columns not in selection
                    if selected_columns is not None and f"{table_name}.{field_name}".lower() not in selected_columns:
                        continue

                    field_type = field_info['type']
                    autoincrement = field_info.get('autoincrement', False)
                    is_pk = field_info.get('primary_key', False)
                    nullable = field_info.get('nullable', True)
                    unique = field_info.get('unique', False)
                    default = field_info.get('default')
                    comment = field_info.get('comment', '')

                    # Handle autoincrement and primary key per dialect
                    if autoincrement:
                        if dialect == 'sqlite':
                            # SQLite requires "INTEGER PRIMARY KEY AUTOINCREMENT"
                            field_type = "INTEGER"
                            is_pk = True  # enforce PK for autoincrement
                        elif dialect == 'postgresql':
                            field_type = "SERIAL"
                        elif dialect == 'mysql':
                            field_type += " AUTO_INCREMENT"
                        elif dialect == 'mssql':
                            field_type += " IDENTITY(1,1)"

                    field_line = f"    {field_name} {field_type}"

                    # Constraints
                    if not nullable:
                        field_line += " NOT NULL"
                    if unique:
                        field_line += " UNIQUE"
                    if default is not None:
                        field_line += f" DEFAULT {default}"

                    # SQLite AUTOINCREMENT primary key inline declaration
                    if dialect == 'sqlite' and is_pk and autoincrement:
                        field_line = f"    {field_name} INTEGER PRIMARY KEY AUTOINCREMENT"
                        # SQLite does not allow adding separate PRIMARY KEY clause for this column
                        primary_keys = []  # handled inline
                    elif is_pk:
                        primary_keys.append(field_name)

                    # Add column comments (for dialects that support comments)
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

                # Add primary key constraint (skip for inline SQLite AUTOINCREMENT case)
                if primary_keys:
                    field_lines.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")

                # Add foreign keys
                for fk in self.foreign_keys:
                    table1, column1, _, table2, column2 = fk
                    if table1.lower() == table_name.lower():
                        if selected_tables is None or \
                        (table1.lower() in selected_tables and table2.lower() in selected_tables):
                            fk_line = f"    CONSTRAINT fk_{table1}_{column1} FOREIGN KEY ({column1}) REFERENCES {table2} ({column2})"
                            if dialect == 'sqlite':
                                # SQLite supports FK syntax, but enforcement is runtime-configurable
                                fk_line += " ON DELETE CASCADE"
                            field_lines.append(fk_line)

                output.append(',\n'.join(field_lines))
                output.append(");")

        ddl = '\n\n'.join(output)

        if dialect == 'sqlite':
            # SQLite requires pragma to enable FK constraints
            ddl = "PRAGMA foreign_keys = ON;\n\n" + ddl

        return ddl