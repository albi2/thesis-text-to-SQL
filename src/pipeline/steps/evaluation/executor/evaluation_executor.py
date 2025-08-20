from context.pipeline_context import PipelineContext
from executor.statistics_manager import EvaluationResult
from util.constants import DatabaseConstants
from util.db.execute import _compare_sqls_outcomes


class EvaluationExecutor:
    def execute(self, pipeline_context: PipelineContext) -> EvaluationResult:
        """
        Compares the selected SQL query with the gold standard query and returns the evaluation result.
        """
        selected_query = pipeline_context.selected_sql_query
        gold_query = pipeline_context.task.sql

        if not selected_query or not gold_query:
            raise ValueError("Selected query or gold query not found in pipeline context.")

        comparison_status = _compare_sqls_outcomes(
            predicted_sql=selected_query.sql,
            ground_sql=gold_query,
            db_path=DatabaseConstants.DB_PATH
        )

        return EvaluationResult(
            question=pipeline_context.task.question,
            evidence=pipeline_context.task.evidence,
            generated_sql=selected_query.sql,
            gold_sql=gold_query,
            comparison_status=comparison_status,
            execution_status=selected_query.status
        )