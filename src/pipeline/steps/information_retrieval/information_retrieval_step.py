from typing import Dict, List, Any
from util.db.database_descriptor import DatabaseDescriptor
from util.db.description_csv import load_database_descriptor
from pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever
from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput
from typing import Optional
import time

class InformationRetrievalStepOutput(PipelineStepOutput):
    def __init__(self, retrieved_context: Dict[str, List[Dict[str, Any]]]):
        self.retrieved_context = retrieved_context


class InformationRetrievalStep(PipelineStep[PipelineContext, InformationRetrievalStepOutput]):
    def __init__(self):
        self.information_retriever = InformationRetriever()

    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[Any] = None) -> Optional[InformationRetrievalStepOutput]:
        context.descriptions_database = load_database_descriptor(context.task.db_id)
        context.schema_engine.mschema.set_database_descriptor(context.descriptions_database)

        keywords_and_phrases = self.information_retriever.extract_keywords(user_query=context.user_query)
        context.keywords_and_phrases = keywords_and_phrases
        
        keywords = keywords_and_phrases.get("keywords", [])
        phrases = keywords_and_phrases.get("phrases", [])

        if not keywords and not phrases:
            print(f"Information retriever failed to extract keywords or phrases!")
            return InformationRetrievalStepOutput(retrieved_context={})
        
        context.relevant_entities = self.information_retriever.retrieve_entities(
            db_id=context.task.db_id,
            phrases=phrases
        )

        retrieved_context = self.information_retriever.retrieve_context(keywords=keywords, task=context.task)
        context.db_schema_per_keyword = retrieved_context
        
        return InformationRetrievalStepOutput(retrieved_context=retrieved_context)