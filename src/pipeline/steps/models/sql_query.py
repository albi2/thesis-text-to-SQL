from dataclasses import dataclass
from pipeline.steps.models.schema_representation import SchemaRepresentation
from util.db.execute import SQLExecInfo


@dataclass
class SQLQuery:
    sql_exec_info: SQLExecInfo
    schema_representation: SchemaRepresentation
    model_key: str

    def to_dict(self):
        return {
            "sql_exec_info": self.sql_exec_info.to_dict(),
            "schema_representation": self.schema_representation.to_dict(),
            "model_key": self.model_key
        }
    
    def to_full_dict(self):
        return {
            "sql_exec_info": self.sql_exec_info.to_dict(),
            "schema_representation": self.schema_representation.to_full_dict(),
            "model_key": self.model_key
        }