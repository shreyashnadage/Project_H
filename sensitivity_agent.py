from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from tools_utility import list_tools as common_tools_list
from react_agent_system_prompts import *
from langgraph.types import Command
from typing import Literal
from sensitivity_xml_tools import list_sensitivity_tools as sensitivity_xml_tool_list
from llm_manager import llm
from ExtendedStatePlanExecute import AgentResponseSchema, PlanExecuteState

all_tools_sensitivity_xml = common_tools_list + sensitivity_xml_tool_list

input_messages = {'messages': [SystemMessage(content=sensitivity_agent_system_prompt_content)]}
sensitivity_agent = create_react_agent(llm,
    tools = all_tools_sensitivity_xml,
    response_format=AgentResponseSchema
)

def sensitivity_agent_node(state: PlanExecuteState) -> Command[Literal["replanner"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = sensitivity_agent.invoke(messages)
    response_structured = response['structured_response']
    return Command(goto="replanner", update={"messages": [
                AIMessage(content=response_structured.summary.strip(), name="sensitivity_agent")
            ], 'past_steps': [(state["next_agent"], response_structured.summary, response_structured.status)]})
