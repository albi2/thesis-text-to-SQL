import json
import multiprocessing
from typing import List
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
from executor.statistics_manager import StatisticsManager
from pipeline.steps.evaluation.evaluation_step import EvaluationStep
from infrastructure.database.database_manager import DatabaseManager
class RunningManager:
    RESULT_ROOT_PATH = "/root/data/results"

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

        db_manager = DatabaseManager()
        database_engine = db_manager.create_engine(task.db_id)
        
        if not database_engine:
            print(f"Failed to create database engine for db_id: {task.db_id}. Skipping task.")
            return
        
        print("ZZZZZ - Created db")


        schema_factory = SchemaEngineFactory()
        schema_engine = schema_factory.create_schema_engine(engine=database_engine, db_name=task.db_id)

        print("ZZZZZ - Created schema engine")


        if not schema_engine:
            print(f"Failed to create SchemaEngine for db_id: {task.db_id}. Skipping task.")
            return

        context = PipelineContext(
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

        pipeline.run(context)
        print("ZZZZZ - Created schema engine")
        
        self.statistics_manager.add_result(context.evaluation_result)
        print(f"Finished pipeline for question_id: {task.question_id}")

    def run_evaluation(self):
        """
        Iterates through the loaded tasks and runs the pipeline for each in a separate process.
        """
        if not self.tasks:
            print("No tasks to run. Please load tasks first.")
            return

        # for task in self.tasks:
        #     result_queue = multiprocessing.Queue()
        #     process = multiprocessing.Process(
        #         target=self.run_pipeline_for_task, 
        #         args=(task, result_queue)
        #     )
        #     process.start()
        #     process.join()  # Wait for THIS process to complete before starting next
            
        # # Collect result from this process
        # if not result_queue.empty():
        #     result = result_queue.get()
        #     self.statistics_manager.add_result(result)


        in_processing_tasks = self.tasks[:7]

        for task in in_processing_tasks:
            self.run_pipeline_for_task(task)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.statistics_manager.save_results(f"{self.RESULT_ROOT_PATH}/evaluation_results_{timestamp}.json")