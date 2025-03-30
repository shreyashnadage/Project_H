from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools_utility import list_tools as common_tools_list
from ore_xml_tools import list_ore_tools as ore_xml_tools_list
from react_agent_system_prompts import *
from ExtendedState import State
from langgraph.types import Command
from typing import Literal
from config_file import file_location_prompt


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


all_tools_list_ore_xml = ore_xml_tools_list + common_tools_list


llm = ChatAnthropic(
    model="claude-3-5-haiku-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)

input_messages = {'messages': [SystemMessage(content=ore_agent_system_prompt_content),SystemMessage(content=file_location_prompt)]}
ore_agent = create_react_agent(llm,
    tools = all_tools_list_ore_xml,
)

def ore_xml_agent_node(state: State) -> Command[Literal["supervisor"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria_current_agent"])]
    messages = {'messages': messages_list}
    response = ore_agent.invoke(messages)
    state["messages"] = messages_list + response["messages"]

    return Command(goto="supervisor", update={"messages": [
                HumanMessage(content=response["messages"][-1].content, name="ore_agent")
            ]})








