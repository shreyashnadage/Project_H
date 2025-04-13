
import os
import shutil
from dotenv import load_dotenv, find_dotenv
from langgraph.checkpoint.memory import MemorySaver
load_dotenv(find_dotenv(), override = True)
from config_file import f_path_in, f_path_out, term_sheet_file


def copy_directory(src_dir):
    dst_dir= os.path.basename(src_dir)+'new'
    dst_dir = os.path.join(os.path.dirname(src_dir), dst_dir)

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        shutil.copy2(s, d)

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        shutil.copy2(s, d)


from langchain_core.messages import HumanMessage
from llm_manager import llm
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
from langchain_community.document_loaders import PyPDFLoader



def load_pdf(file_name):
    loader = PyPDFLoader(file_name)
    pages = []
    doc_data = ''
    for page in loader.lazy_load():
        pages.append(page)
        doc_data += page.page_content + '\n'
    return pages, doc_data

# termsheet_path = r'D:\Project_H\usd-inr-ccs-fixed-float.pdf'
# term_sheet_file.term_sheet_data = load_pdf(termsheet_path)[1]

# Set up memory
memory = MemorySaver()
thread_config = {"configurable": {"thread_id": "1"}}


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
# user_query = """keep only npv analytics and remove all other analytics. and then run ore"""
# user_query = """Please compute var for given setup and analyze the results from var"""
# user_query = """analyze the stress scenario results. describe how it impacted the trades in portfolio. provide a detailed summary with plots and tabular analysis."""
# user_query = """Add scenario where EUR discounting curve is shocked parallely by 5bps.run ore for stress test and analyze the stress test results"""
# user_query = """Compute exposure and then report peak exposure for each trades. plot the exposures."""
# user_query = """add exposure analytics and turn it on."""
# user_query = """remove exposure analytics then add it back.then run ore to produce exposure results and then analyze the results of exposure results and provide summary of peak exposure."""
# user_query = """analyze results for exposure. provide a detailed summary report with plots for exposure."""
# user_query = """add a stress scenario where eur discounting curve is shocked parallely by 5% up and other scenario with 5% down. run ore for stress test and analyze the stress test results."""
# user_query = """convert following into trade and add it to portfolio.xml. trade\nThis USD/INR cross currency swap trade, effective October 12, 2023, and expiring October 12, 2028, involves JPMorgan (Party A) and a counterparty (Party B). It has a USD Notional Amount of $50,000,000 and an INR Notional Amount based on a USD/INR spot rate of 83.25. In this fixed-to-float swap, Party A pays USD-SOFR-COMPOUND annually on the USD amount (A/360, adjusted), with payments starting October 12, 2024. Party B pays a fixed 7.30% semi-annually on the INR amount (A/365F, adjusted), starting April 12, 2024. Initial exchange on the Effective Date involves Party A paying INR and Party B paying USD notional amounts; the reverse occurs at termination. Governed by English law under ISDA, with JPMorgan as Calculation Agent, the swap hedges Party B’s USD floating rate liability into an INR fixed rate liability, maturing October 12, 2028."""

# # test = []
# for s in main_graph.stream(
#     {"messages": [HumanMessage(content=user_query)],"input_path":f_path_in,"output_path":f_path_out,"user_query": user_query}):
#     print(s)
#     print("---")

# ab= 0 


import streamlit as st
st.set_page_config(page_title="ORE Agent", page_icon="Logo.jpg", layout="wide")
st.logo(
    "Logo.jpg",
    link="https://quantcatalysts.com",
    icon_image="Logo.jpg",
)

header_col, _, stop_button_col = st.columns(3)
with header_col:
    st.header("Risk Engine Copilot", divider=True)

with st.sidebar:
    uploaded_file = st.file_uploader("Upload Term Sheet", type=["pdf"])
    if uploaded_file is not None:
        term_sheet_file.term_sheet_data = load_pdf(uploaded_file.name)[1]

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message(message["role"]):
            stream = message["content"]
            node_name = next(iter(stream))
            if node_name in ['planner', 'replanner']:
                with st.status("Creating plan..."):

                    if (stream[node_name].get('plan_steps') is not None) and (stream[node_name].get('action') is None):
                        for step in stream[node_name]['plan_steps']:
                            st.write(f"Agent: {step[0]} | Task: {step[1]} | Stopping Criteria: {step[2]}")
                    
                if stream[node_name].get('action') == "FINISH":
                    with st.expander('See detailed report...'):
                        st.markdown(stream[node_name].get('markdown_report'))
                    st.success("Completed successfully.", icon="✅")
            elif (node_name=='router'):
                if stream[node_name].get('action') == "FINISH":
                    with st.expander('See detailed report...'):
                        st.markdown(stream[node_name].get('markdown_report'))
                    st.success("Completed successfully.", icon="✅")
                elif stream[node_name] is not None:
                    with st.spinner('Working on task:'):
                        st.write(f"👤 {stream['router']['next_agent']} 🎯 {stream['router']['next_task']}  ⏹️ {stream['router']['stopping_criteria']}")
            else:
                summary_response = stream[node_name]['past_steps'][0][1]
                with st.expander('See detailed report...'):
                    st.markdown(summary_response)
                    plot_dict = stream[node_name].get('plot_file_dict')
                    if plot_dict is not None:
                        for plot_name, plot_description in plot_dict.items():
                            st.image(plot_name, caption=plot_description)

if user_prompt := st.chat_input("What do you want to get done from ORE today?"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    with st.chat_message("assistant"):
        for stream in main_graph.stream(
        {"messages": [HumanMessage(content=user_prompt)],"input_path":f_path_in,"output_path":f_path_out,"user_query": user_prompt}):
            node_name = next(iter(stream))
            print(stream)
            if node_name in ['planner', 'replanner']:
                with st.status("Creating plan..."):

                    if (stream[node_name].get('plan_steps') is not None) and (stream[node_name].get('action') is None):
                        for step in stream[node_name]['plan_steps']:
                            st.write(f"Agent: {step[0]} | Task: {step[1]} | Stopping Criteria: {step[2]}")
                    
                if stream[node_name].get('action') == "FINISH":
                    with st.expander('See detailed report...'):
                        st.markdown(stream[node_name].get('markdown_report'))
                    st.success("Completed successfully.", icon="✅")
            elif (node_name=='router'):
                if stream[node_name].get('action') == "FINISH":
                    with st.expander('See detailed report...'):
                        st.markdown(stream[node_name].get('markdown_report'))
                    st.success("Completed successfully.", icon="✅")
                elif stream[node_name] is not None:
                    with st.spinner('Working on task:'):
                        st.write(f"👤 {stream['router']['next_agent']} 🎯 {stream['router']['next_task']}  ⏹️ {stream['router']['stopping_criteria']}")
            else:
                summary_response = stream[node_name]['past_steps'][0][1]
                with st.expander('See detailed report...'):
                    st.markdown(summary_response)
                    plot_dict = stream[node_name].get('plot_file_dict')
                    try:
                        if plot_dict is not None:
                            for plot_name, plot_description in plot_dict.items():
                                st.image(plot_name, caption=plot_description)
                    except Exception as e:
                        pass
    st.session_state.messages.append({"role": "assistant", "content": stream})