import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from util.db.execute import SQLExecStatus


@dataclass
class EvaluationResult:
    """
    Holds the detailed evaluation results for a single task.
    """
    question: str
    evidence: Optional[str]
    generated_sql: str
    gold_sql: str
    comparison_status: int  # 1 for equivalent, 0 for not equivalent
    execution_status: SQLExecStatus


@dataclass
class StatisticsManager:
    """
    Manages and aggregates evaluation results for all processed tasks.
    """
    results: List[EvaluationResult] = field(default_factory=list)

    def add_result(self, result: EvaluationResult):
        """
        Adds a new evaluation result to the manager.
        """
        self.results.append(result)

    def save_results(self, output_path: str):
        """
        Saves the aggregated results to a JSON file.
        """
        # Convert SQLExecStatus enum to its string value for serialization
        results_data = []
        for res in self.results:
            res_dict = asdict(res)
            if res.execution_status is not None:
                res_dict['execution_status'] = res.execution_status.value 
            results_data.append(res_dict)

        with open(output_path, "w") as f:
            json.dump(results_data, f, indent=4)