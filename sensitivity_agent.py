from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools_utility import list_tools as common_tools_list
from react_agent_system_prompts import *
from ExtendedState import State
from langgraph.types import Command
from typing import Literal
from config_file import file_location_prompt
from sensitivity_xml_tools import list_sensitivity_tools as sensitivity_xml_tool_list
from pydantic import BaseModel, Field
from llm_manager import llm
from summary_node import summary_node

llm = ChatAnthropic(
    model="claude-3-5-haiku-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)

all_tools_sensitivity_xml = common_tools_list + sensitivity_xml_tool_list

input_messages = {'messages': [SystemMessage(content=sensitivity_agent_system_prompt_content),SystemMessage(content=file_location_prompt)]}
sensitivity_agent = create_react_agent(llm,
    tools = all_tools_sensitivity_xml
)

class Summary(BaseModel):
    summary: str = Field(description="Summary of the tasks performed so far and also past summary. This is to keep track of past actions and thier outcomes and also to provide context to next task. Should be blank if there is no task performed so far, Should be clear and consise eg: 1. <task performed>:<task outcome>, 2. <task performed>:<task outcome>")
    is_completed: Literal["True", "False"] = Field(description="Is the task completed or not. Should be True if the task is completed, False otherwise.")

def sensitivity_agent_node(state: State) -> Command[Literal["supervisor"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = sensitivity_agent.invoke(messages)
    state["messages"] = messages_list + response["messages"]
    response_txt = summary_node(response, state)
    return Command(goto="supervisor", update={"messages": [
                HumanMessage(content=response_txt, name="sensitivity_agent")
            ]})
