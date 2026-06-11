from __future__ import annotations

import json
import os
import sys
import asyncio
from pathlib import Path
from typing import Any, Literal

import httpx
import yaml
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
	OpenAIChatCompletion,
	OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.functions import KernelArguments

from travel_planner.models.MissingInformation import MissingInformationResult
from travel_planner.models.relevance import RelevanceResult
from travel_planner.models.TripDetails import TripDetailsResult
from travel_planner.models.FollowUpQuestions import FollowUpQuestionsResult
from travel_planner.models.Pipeline import PipelineResult
from travel_planner.registry.agent_registry import get_agent_url
from travel_planner.Utils.utils_orchestrator import _load_json, _result_to_text

BASE_DIR = Path(__file__).resolve().parents[3]
with open(BASE_DIR / "prompts.yaml", "r", encoding="utf-8") as f:
	PROMPTS = yaml.safe_load(f)
load_dotenv(BASE_DIR / ".env")
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
	raise RuntimeError("GROQ_API_KEY is missing.")
MODEL = "llama-3.3-70b-versatile"
SERVICE_ID = "groq"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


# relevance = RelevanceResult(relevant=True, reason="The user's input is relevant to travel planning.", humorous_reply="Why did the traveler bring a ladder? Because they wanted to reach new heights in their itinerary!").dict()
# print (relevance)
# missing_information = MissingInformationResult(does_have_information=True, missing_information=[]).dict()
# print(missing_information["missing_information"])
# print(type(missing_information["missing_information"]))

class TravelAgentOrchestrator:
    def __init__(self):

        self.kernel = Kernel()
        client = AsyncOpenAI(api_key=API_KEY, base_url=GROQ_BASE_URL)
        self.kernel.add_service(
            OpenAIChatCompletion(
                ai_model_id=MODEL,
                service_id=SERVICE_ID,
                async_client=client
            )
        )
        self.settings = OpenAIChatPromptExecutionSettings(
            temperature=0,
            service_id=SERVICE_ID,
            response_format={"type": "json_object"}
        )
    async def run(self, user_input: str) -> PipelineResult:
        relevance = await self._invoke_agent(
            prompt=PROMPTS["relevance_agent"]["content"],
            model=RelevanceResult,
            arguments={"input": user_input},
            agent_name="relevance_agent",
        )
        relevance = relevance.model_validate({
            **relevance.model_dump(),
             "user_input": user_input
       })   
        
        print(relevance)
        if not relevance.relevant:
            return PipelineResult(
                stage="irrelevant",
                user_input=user_input,
                relevant=False,
                humorous_reply=relevance.humorous_reply,
            ).model_dump()
        _summary = json.dumps(relevance.summary)
        MissedInformation = await self._invoke_agent(
            prompt=PROMPTS["missing_information_agent"]["content"],
            model=MissingInformationResult,
            arguments={"input": _summary},
            agent_name="missing_information_agent",
        )
        print(MissedInformation)
        if not MissedInformation.does_have_all_information or len(MissedInformation.missing_information) > 0:
            questions = await self._invoke_agent(
                prompt=PROMPTS["follow_up_questions_agent"]["content"],
                model=FollowUpQuestionsResult,
                arguments={
                    "input": _summary,
                    "missing_information": json.dumps(MissedInformation.missing_information),
                    "extracted_data": json.dumps(relevance.summary),
                },
                agent_name="follow_up_questions_agent",
            )
            print(questions)
            return PipelineResult(
                stage="needs_info",
                user_input=user_input,
                relevant=True,
                has_required_information=False,
                missing_information=MissedInformation.missing_information,
                questions=questions.questions,
            ).model_dump()
        
        else:
            trip_details = await self._invoke_agent(
                prompt=PROMPTS["trip_details_agent"]["content"],
                model=TripDetailsResult,
                arguments={
                     "extracted_data": _summary,
                     },
                agent_name="trip_details_agent",
            )
            print(trip_details)
            itinerary = await self._get_places_recommendations(trip_details)
            return PipelineResult(
                stage="ready",
                user_input=user_input,
                relevant=True,
                has_required_information=True,
                missing_information=[],
                trip_data=trip_details.model_dump(),
                itinerary=itinerary,
            ).model_dump()
        
  
    async def _get_places_recommendations(self, trip_details: TripDetailsResult) -> list[dict]:
        places_url = get_agent_url("places")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{places_url}/recommend",
                    json={
                        "where": trip_details.where,
                        "interests": trip_details.interests,
                        "duration": trip_details.duration,
                    },
                    timeout=15.0,
                )
            response.raise_for_status()
            return response.json().get("itinerary", [])
        except Exception as e:
            print(f"orchestrator: places agent call failed: {e}")
            return []

    async def _invoke_agent(
              self,
              prompt: str,
              model: BaseModel,
              arguments: dict[str, Any],
              agent_name: str
            ) -> BaseModel:
            response = await self.kernel.invoke_prompt(
                prompt,
                arguments=KernelArguments(**arguments),
                settings=self.settings,
            )
            raw_output = _result_to_text(response)
            return await self._validate_or_repair(
                raw_output=raw_output,
                model=model,
                agent_name=agent_name,
                original_input=arguments,
            )
    
    async def _validate_or_repair(
            self,
            *,
            raw_output: str,
            model: type[BaseModel],
            agent_name: str,
            original_input: dict[str, Any],
        ) -> BaseModel:
            try:
                parsed = _load_json(raw_output)
                return model.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as first_error:
                repaired_output = await self.kernel.invoke_prompt(
                    PROMPTS["schema_debugger_agent"]["content"],
                    arguments=KernelArguments(
                        agent_name=agent_name,
                        broken_output=raw_output,
                        expected_schema=json.dumps(model.model_json_schema(), indent=2),
                        validation_error=str(first_error),
                        original_input=json.dumps(original_input, indent=2),
                    ),
                    settings=self.settings,
                )
                repaired_text = _result_to_text(repaired_output)
                repaired_parsed = _load_json(repaired_text)
                return model.model_validate(repaired_parsed)

              
if __name__ == "__main__":
    TravelAgent = TravelAgentOrchestrator()
    asyncio.run(
        TravelAgent.run("I want to visit Paris in 5th May for 5 days, and I love art and food. Can you help me plan a trip?")
    )