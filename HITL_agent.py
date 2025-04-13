from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from react_agent_system_prompts import *
from langgraph.types import Command, interrupt
from typing import Literal
from llm_manager import llm
from ExtendedStatePlanExecute import AgentResponseSchema, PlanExecuteState
from pydantic import BaseModel

class HITLQuery(BaseModel):
    query: str = Field(description="Query to ask to human")
    

def HITL_agent_node(state: PlanExecuteState) -> Command[Literal["replanner"]]:
    messages_list = [HumanMessage(content='\n\nQuery to ask to human:\n' + state["next_task"]+"guidance for answering question: " + state["stopping_criteria"] + "\n\ndetailed context:\n" + state["detailed_context"]+"\n\n frame this into a question to ask to human.")]
    messages = {'messages': messages_list}
    response = llm.with_structured_output(HITLQuery).invoke(messages)
    human_response = interrupt(response.query)
    response_structured = response['structured_response']
    return Command(goto="replanner", update={"messages": [
                AIMessage(content=response_structured.summary.strip(), name="ore_xml_agent")
            ], 'past_steps': [(state["next_agent"], response_structured.summary, response_structured.status)], 'human_feedback'})