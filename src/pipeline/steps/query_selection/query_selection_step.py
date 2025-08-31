from typing import Optional, Any
from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput
from pipeline.steps.query_selection.executor.query_selection_executor import QuerySelectionExecutor
from util.db.execute import SQLExecInfo


class QuerySelectionStepOutput(PipelineStepOutput):
    def __init__(self, selected_query: SQLExecInfo):
        self.selected_query = selected_query


class QuerySelectionStep(PipelineStep[PipelineContext, QuerySelectionStepOutput]):
    def __init__(self):
        self.executor = QuerySelectionExecutor()

    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[Any] = None) -> Optional[QuerySelectionStepOutput]:
        print("------------------ QUERY SELECTION STEP ---------------------- \n")
        if context.generated_sql_queries is None or len(context.generated_sql_queries) == 0:
            return None

        selected_query = self.executor.execute(
            pipeline_context=context
        )
        context.selected_sql_query = selected_query
        
        return QuerySelectionStepOutput(selected_query=selected_query)