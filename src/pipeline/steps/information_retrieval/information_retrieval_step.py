from typing import Dict, List, Any
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
        keywords_and_phrases = self.information_retriever.extract_keywords(user_query=context.user_query)
        keywords = keywords_and_phrases.get("keywords", [])
        
        retrieved_context = self.information_retriever.retrieve_context(keywords=keywords, question=context.user_query)
        context.db_schema_per_keyword = retrieved_context

        print("--------------- WAITING 10 SECONDS ----------------------")
        time.sleep(10)
        
        return InformationRetrievalStepOutput(retrieved_context=retrieved_context)