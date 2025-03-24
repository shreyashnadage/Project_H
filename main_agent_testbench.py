
import inspect
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools_utility import list_tools as common_tools_list
from ore_xml_tools import list_ore_tools as ore_xml_tools_list
from sensitivity_xml_tools import list_sensitivity_tools as sensitivity_xml_tool_list
from react_agent_system_prompts import *
import mlflow
import getpass
import os
import shutil
# Enabling tracing for LangGraph (LangChain)
mlflow.langchain.autolog()

# Optional: Set a tracking URI and an experiment
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("LangGraph")


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

_set_env("ANTHROPIC_API_KEY")
_set_env('LANGSMITH_API_KEY')



from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from supervisor_node import make_supervisor_node
from ore_xml_agent import ore_xml_agent_node
from langgraph.graph import StateGraph, MessagesState, START
from sensitivity_agent import sensitivity_agent_node
from ore_execution_agent import ore_execution_agent_node


llm = ChatAnthropic(
    model="claude-3-5-haiku-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)

class State(MessagesState):
    next: str

main_supervisor_node = make_supervisor_node(llm=llm, state=State, members=["ore_xml_agent", "sensitivity_agent", "ore_execution_agent"])

main_agent_builder = StateGraph(State)
main_agent_builder.add_node("supervisor", main_supervisor_node)
main_agent_builder.add_node("ore_xml_agent", ore_xml_agent_node)
main_agent_builder.add_node("sensitivity_agent", sensitivity_agent_node)
main_agent_builder.add_node("ore_execution_agent", ore_execution_agent_node)

main_agent_builder.add_edge(START, "supervisor")
main_graph = main_agent_builder.compile()


ascii_representation = main_graph.get_graph().print_ascii()
print(ascii_representation)

for s in main_graph.stream(
    {"messages": [("user", "What are the current analytics in ore.xml?")]}
):
    print(s)
    print("---")