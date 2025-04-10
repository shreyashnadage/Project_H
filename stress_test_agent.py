from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from tools_utility import list_tools as common_tools_list
from react_agent_system_prompts import *
from langgraph.types import Command
from typing import Literal
from stress_test_xml_tools import list_stress_test_tools as stress_test_xml_tool_list
from react_agent_system_prompts import stress_config_agent_system_prompt_content
from llm_manager import llm
from ExtendedStatePlanExecute import AgentResponseSchema, PlanExecuteState

all_tools_stress_test_xml = common_tools_list + stress_test_xml_tool_list

input_messages = {'messages': [SystemMessage(content=stress_config_agent_system_prompt_content)]}
stress_test_agent = create_react_agent(llm,
    tools = all_tools_stress_test_xml,
    response_format=AgentResponseSchema
)

def stress_test_agent_node(state: PlanExecuteState) -> Command[Literal["replanner"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content='\n\nTask: ' + state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = stress_test_agent.invoke(messages)
    response_structured = response['structured_response']
    return Command(goto="replanner", update={"messages": [
                AIMessage(content=response_structured.summary.strip(), name="stress_test_agent")
            ], 'past_steps': [(state["next_agent"], response_structured.summary, response_structured.status)]})
