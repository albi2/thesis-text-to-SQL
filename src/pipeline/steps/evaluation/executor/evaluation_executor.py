from context.pipeline_context import PipelineContext
from executor.statistics_manager import EvaluationResult
from util.constants import DatabaseConstants
from util.db.execute import compare_sqls_outcomes


class EvaluationExecutor:
    def execute(self, pipeline_context: PipelineContext) -> EvaluationResult:
        """
        Compares the selected SQL query with the gold standard query and returns the evaluation result.
        """
        selected_query = pipeline_context.selected_sql_query
        gold_query = pipeline_context.task.SQL

        if not selected_query or not gold_query:
            return EvaluationResult(
                question=pipeline_context.task.question,
                evidence=pipeline_context.task.evidence,
                generated_sql=None,
                gold_sql=gold_query,
                comparison_status=0,
                execution_status=None
            )

        comparison_status = compare_sqls_outcomes(
            predicted_sql=selected_query.sql,
            ground_sql=gold_query,
            db_path=DatabaseConstants.DB_PATH,
            engine=pipeline_context.db_engine
        )

        return EvaluationResult(
            question=pipeline_context.task.question,
            evidence=pipeline_context.task.evidence,
            generated_sql=selected_query.sql,
            gold_sql=gold_query,
            comparison_status=comparison_status,
            execution_status=selected_query.status
        )