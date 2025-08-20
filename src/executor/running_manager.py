import json
import multiprocessing
from typing import List
from sqlalchemy.engine import Engine
from datetime import datetime

from components.schema.schema_engine_factory import SchemaEngineFactory
from context.pipeline_context import PipelineContext
from pipeline.pipeline import Pipeline
from pipeline.steps.information_retrieval.information_retrieval_step import InformationRetrievalStep
from pipeline.steps.print_output.print_output_step import PrintOutputStep
from pipeline.steps.schema_filter.schema_filter_step import SchemaFilterStep
from pipeline.steps.sql_generation.sql_generation_step import SQLGenerationStep
from pipeline.steps.query_selection.query_selection_step import QuerySelectionStep
from executor.task_model import Task
from infrastructure.database.database_manager import db_manager
from executor.statistics_manager import StatisticsManager
from pipeline.steps.evaluation.evaluation_step import EvaluationStep

class RunningManager:
    RESULT_ROOT_PATH = "results"

    """
    Manages the process of loading tasks and running the evaluation pipeline for each.
    """
    def __init__(self, dataset_path: str):
        """
        Initializes the RunningManager with the path to the dataset.

        Args:
            dataset_path: The path to the JSON file containing the tasks.
        """
        self.dataset_path = dataset_path
        self.tasks: List[Task] = []
        self.statistics_manager = StatisticsManager()

    def load_tasks(self):
        """
        Loads tasks from the dataset file into a list of Task objects.
        """
        try:
            with open(self.dataset_path, "r") as f:
                tasks_data = json.load(f)
            self.tasks = [Task(**task_data) for task_data in tasks_data]
            print(f"Loaded {len(self.tasks)} tasks from {self.dataset_path}")
        except FileNotFoundError:
            print(f"Error: {self.dataset_path} not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.dataset_path}.")

    def run_pipeline_for_task(self, task: Task):
        """
        Initializes and runs the SQL generation pipeline for a single task.
        This method is designed to be run in a separate process.
        """
        print(f"Running pipeline for question_id: {task.question_id} on db_id: {task.db_id}")
        
        database_engine: Engine | None = db_manager._engine

        if not database_engine:
            print(f"Failed to create database engine for db_id: {task.db_id}. Skipping task.")
            return

        schema_factory = SchemaEngineFactory()
        schema_engine = schema_factory.create_schema_engine(engine=database_engine)

        if not schema_engine:
            print(f"Failed to create SchemaEngine for db_id: {task.db_id}. Skipping task.")
            return

        initial_context = PipelineContext(
            task=task,
            db_engine=database_engine,
            schema_engine=schema_engine
        )

        pipeline = Pipeline[PipelineContext].Builder() \
            .add_step(InformationRetrievalStep()) \
            .add_step(PrintOutputStep()) \
            .add_step(SchemaFilterStep()) \
            .add_step(PrintOutputStep()) \
            .add_step(SQLGenerationStep()) \
            .add_step(PrintOutputStep()) \
            .add_step(QuerySelectionStep()) \
            .add_step(PrintOutputStep()) \
            .add_step(EvaluationStep()) \
            .build()

        pipeline.run(initial_context)
        
        self.statistics_manager.add_result(initial_context.evaluation_result)
        
        print(f"Finished pipeline for question_id: {task.question_id}")

    def run_evaluation(self):
        """
        Iterates through the loaded tasks and runs the pipeline for each in a separate process.
        """
        if not self.tasks:
            print("No tasks to run. Please load tasks first.")
            return

        for task in self.tasks:
            process = multiprocessing.Process(target=self.run_pipeline_for_task, args=(task,))
            process.start()
            process.join()  # Wait for the process to complete before starting the next one
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.statistics_manager.save_results(f"{self.RESULT_ROOT_PATH}/evaluation_results_{timestamp}.json")