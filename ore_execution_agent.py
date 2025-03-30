from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from ore_execution_tools import list_ore_tools as ore_exe_tools_list
from react_agent_system_prompts import *
from ExtendedState import State
from langgraph.types import Command
from typing import Literal
from config_file import file_location_prompt
from summary_node import summary_node
from llm_manager import llm


input_messages = {'messages': [SystemMessage(content=ore_execution_agent_system_prompt_content),SystemMessage(content=file_location_prompt)]}
ore_execution_agent = create_react_agent(llm,
    tools = ore_exe_tools_list,
)

def ore_execution_agent_node(state: State) -> Command[Literal["supervisor"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = ore_execution_agent.invoke(messages)
    state["messages"] = messages_list + response["messages"]
    response_txt = summary_node(response, state)
    return Command(goto="supervisor", update={"messages": [
                HumanMessage(content=response_txt, name="ore_execution_agent")
            ]})


# test = ore_execution_agent.invoke({'messages': [SystemMessage(content=ore_execution_agent_system_prompt_content),SystemMessage(content=file_location_prompt)] + [HumanMessage(content="run ore with ore.xml")]})

# test1 = 0







