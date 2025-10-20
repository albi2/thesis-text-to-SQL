from dataclasses import dataclass
from pipeline.steps.models.schema_representation import SchemaRepresentation
from util.db.execute import SQLExecInfo

@dataclass
class SQLQuery:
    sql_exec_info: SQLExecInfo
    schema_representation: SchemaRepresentation
    model_key: str
    prompting: str
    score: int = 0
    cluster_size: int = 1
    score_cot: str = ''

    def to_dict(self):
        return {
            "sql_exec_info": self.sql_exec_info.to_dict(),
            "schema_representation": self.schema_representation.to_dict(),
            "model_key": self.model_key,
            "prompting": self.prompting,
            "score": self.score,
            "score_cot": self.score_cot
        }
    
    def to_full_dict(self):
        return {
            "sql_exec_info": self.sql_exec_info.to_dict(),
            "schema_representation": self.schema_representation.to_full_dict(),
            "model_key": self.model_key,
            "prompting": self.prompting,
            "score": self.score,
            "score_cot": self.score_cot
        }