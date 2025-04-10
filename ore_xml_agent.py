from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from tools_utility import list_tools as common_tools_list
from ore_xml_tools import list_ore_tools as ore_xml_tools_list
from react_agent_system_prompts import *
from langgraph.types import Command
from typing import Literal
from llm_manager import llm
from ExtendedStatePlanExecute import AgentResponseSchema, PlanExecuteState


all_tools_list_ore_xml = ore_xml_tools_list + common_tools_list



input_messages = {'messages': [SystemMessage(content=ore_xml_agent_system_prompt_content)]}
ore_xml_agent = create_react_agent(llm,
    tools = all_tools_list_ore_xml,
    response_format=AgentResponseSchema
)

def ore_xml_agent_node(state: PlanExecuteState) -> Command[Literal["replanner"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content='\n\nTask: ' + state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = ore_xml_agent.invoke(messages)
    response_structured = response['structured_response']
    return Command(goto="replanner", update={"messages": [
                AIMessage(content=response_structured.summary.strip(), name="ore_xml_agent")
            ], 'past_steps': [(state["next_agent"], response_structured.summary, response_structured.status)]})








