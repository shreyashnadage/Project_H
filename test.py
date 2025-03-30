
import inspect
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from react_agent_system_prompts import *
from members_details import members
import getpass
import os
import shutil
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override = True)



def copy_directory(src_dir):
    dst_dir= os.path.basename(src_dir)+'new'
    dst_dir = os.path.join(os.path.dirname(src_dir), dst_dir)

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        shutil.copy2(s, d)

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


from langchain_core.messages import HumanMessage
from llm_manager import llm
from supervisor_node import make_supervisor_node
from ore_xml_agent import ore_xml_agent_node
from langgraph.graph import StateGraph, MessagesState, START
from sensitivity_agent import sensitivity_agent_node
from ore_execution_agent import ore_execution_agent_node
from ExtendedState import State


main_supervisor_node = make_supervisor_node(llm=llm, state=State, members=members)

main_agent_builder = StateGraph(State)
main_agent_builder.add_node("supervisor", main_supervisor_node)
main_agent_builder.add_node("ore_xml_agent", ore_xml_agent_node)
main_agent_builder.add_node("sensitivity_agent", sensitivity_agent_node)
main_agent_builder.add_node("ore_execution_agent", ore_execution_agent_node)

main_agent_builder.add_edge(START, "supervisor")
main_graph = main_agent_builder.compile()


# test = main_supervisor_node( {"messages": [("user", )]})


ascii_representation = main_graph.get_graph().print_ascii()
print(ascii_representation)

user_query = """What is shock applied to EUR discounting curve. If the shock is 1bps leave as it is else change it to 2bps. After that run the ore to compute npv and sensitivity results."""

for s in main_graph.stream(
    {"messages": [("user", user_query)]}
):
    print(s)
    print("---")