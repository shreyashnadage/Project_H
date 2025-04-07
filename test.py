
from langchain_core.messages import HumanMessage
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
from portfolio_xml_agent import portfolio_xml_agent_node
from stress_test_agent import stress_test_agent_node
from ExtendedState import State
from analysis_agent import analysis_agent_node
from planner_node import planner_node, replanner_node
from router_node import router_node
from ExtendedStatePlanExecute import PlanExecuteState
from streamlit_pretty_printer_library import printer_functions_dict

# main_supervisor_node = make_supervisor_node(llm=llm, state=State, members=members)

# main_agent_builder = StateGraph(State)
# main_agent_builder.add_node("supervisor", main_supervisor_node)
# main_agent_builder.add_node("ore_xml_agent", ore_xml_agent_node)
# main_agent_builder.add_node("sensitivity_agent", sensitivity_agent_node)
# main_agent_builder.add_node("ore_execution_agent", ore_execution_agent_node)
# main_agent_builder.add_node("analysis_agent", analysis_agent_node)

# main_agent_builder.add_edge(START, "supervisor")
# main_graph = main_agent_builder.compile()


main_planner_node = planner_node
main_agent_builder = StateGraph(PlanExecuteState)
main_agent_builder.add_node("planner", main_planner_node)
main_agent_builder.add_node("ore_xml_agent", ore_xml_agent_node)
main_agent_builder.add_node("sensitivity_agent", sensitivity_agent_node)
main_agent_builder.add_node("ore_execution_agent", ore_execution_agent_node)
main_agent_builder.add_node("analysis_agent", analysis_agent_node)
main_agent_builder.add_node("stress_test_agent", stress_test_agent_node)
main_agent_builder.add_node("portfolio_xml_agent", portfolio_xml_agent_node)
main_agent_builder.add_node("replanner", replanner_node)
main_agent_builder.add_node("router", router_node)
main_agent_builder.add_edge(START, "planner")
main_agent_builder.add_edge("planner", "router")
main_graph = main_agent_builder.compile()


# ascii_representation = main_graph.get_graph().print_ascii()
# print(ascii_representation)

# user_query = """Give me analysis of exposure of 20Y swap, focus on exposure"""
# user_query = """Get all active analytics present in the ore.xml file. Check if sensitivity analytics is present if not add it to ore.xml. run ore and then analyze exposure for 20year swap from results."""
# user_query = """Check the shocks applied to EUR discounting curve. change it to 2%. Compute sensitivity for portfolio by running ore. Then check the results of sensitivity."""
# user_query = """Compute npv for the portfolio and then tell me the npv of the portfolio.Then also analyze the exposure of the trade in portfolio. I want to know the maximum exposure of the trades."""
# user_query = """Twist the term structure of EUR discounting curve by 2% in short term and to 0% in longterm.Describe all scenarios in stress test configuration.Then analysze the results of stress test by running ore."""
# user_query = """Create only one new trade swap trade with float(EUR) fixed(GBP) legs in the portfolio.xml file. run ore to compute npv. make your own assumptions."""

# test = []
# for s in main_graph.stream(
#     {"messages": [HumanMessage(content=user_query)],"input_path":r"D:\Project_H\Examples\Example_1\Inputnew","output_path":r"D:\Project_H\Examples\Example_1\Output","user_query": user_query}):
#     print(s)
#     test.append(s)
#     print("---")

# ab= 0 

import streamlit as st
st.set_page_config(page_title="ORE Agent", page_icon="Logo.jpg", layout="wide")
# st.image("Logo.jpg",width = 100)
st.title("Project Hanumaan")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        for stream in main_graph.stream(
        {"messages": [HumanMessage(content=user_prompt)],"input_path":r"D:\Project_H\Examples\Example_1\Inputnew","output_path":r"D:\Project_H\Examples\Example_1\Output","user_query": user_prompt}):
            node_name = next(iter(stream))
            if node_name in ['planner', 'replanner']:
                with st.status("Creating plan..."):

                    if (stream[node_name].get('plan_steps') is not None) and (stream[node_name].get('action') is None):
                        for step in stream[node_name]['plan_steps']:
                            st.write(f"Agent: {step[0]} | Task: {step[1]} | Stopping Criteria: {step[2]}")
                    
                if stream[node_name].get('action') == "FINISH":
                    st.markdown(stream[node_name].get('markdown_report'))
                    st.success("Completed successfully.", icon="✅")
            elif (node_name=='router'):
                if stream[node_name].get('action') == "FINISH":
                    st.markdown(stream[node_name].get('markdown_report'))
                    st.success("Completed successfully.", icon="✅")
                elif stream[node_name] is not None:
                    with st.spinner(f"Agent {stream['router']['next_agent']} is working on {stream['router']['next_task']} with stopping criteria {stream['router']['stopping_criteria']}"):
                        pass
            else:
                summary_response = stream[node_name]['past_steps'][0][1]
                st.markdown(summary_response)
            st.session_state.messages.append({"role": "assistant", "content": stream})