from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from react_agent_system_prompts import analysis_agent_system_prompt_content
from ExtendedState import State
from langgraph.types import Command
from typing import Literal
from config_file import file_location_prompt
from analysis_agent_tools import list_analysis_tools
from llm_manager import llm
from summary_node import summary_node



input_messages = {'messages': [SystemMessage(content=analysis_agent_system_prompt_content),SystemMessage(content=file_location_prompt)]}
analysis_agent = create_react_agent(llm,
    tools = list_analysis_tools
)


def analysis_agent_node(state: State) -> Command[Literal["supervisor"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = analysis_agent.invoke(messages)
    state["messages"] = messages_list + response["messages"]
    response_txt = response["messages"][-1].content
    summary = summary_node({"messages": [response["messages"][-1]]}, state)
    summary = summary +'\nHere is the final analysis:\n'+ response_txt
    return Command(goto="supervisor", update={"messages": [
                HumanMessage(content=summary, name="analysis_agent")
            ]})
