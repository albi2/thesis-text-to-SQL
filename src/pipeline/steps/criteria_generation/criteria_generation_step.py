from typing import Optional, Any
from components.models.api_model_facade import ApiModelFacade
from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput
from prompts.criteria_generation import PROMPT as CRITERIA_GENERATION_PROMPT
import re

class CriteriaGenerationStepOutput(PipelineStepOutput):
    def __init__(self, criteria: str):
        self.criteria = criteria

class CriteriaGenerationStep(PipelineStep[PipelineContext, CriteriaGenerationStepOutput]):
    def __init__(self):
        self.api_model = ApiModelFacade()

    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[Any] = None) -> Optional[CriteriaGenerationStepOutput]:
        criteria_prompt = CRITERIA_GENERATION_PROMPT.format(
            QUESTION=context.user_query,
            HINT=getattr(context, 'hint', '')
        )
        
        query_chain = self.api_model.get_chain()
        criteria_response = self.api_model.call(query_chain, {"user_prompt": criteria_prompt})
        
        try:
            match = re.search(r"<CRITERIA>(.*)</CRITERIA>", criteria_response, re.DOTALL)
            if match:
                criteria = match.group(1).strip()
            else:
                criteria = criteria_response
        except Exception as e:
            print(f"Could not parse criteria from model response: {e}")
            criteria = criteria_response
            
        context.query_evaluation_criteria = criteria
        return CriteriaGenerationStepOutput(criteria=criteria)