from sys import prefix
from llm_manager import llm
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd
import os
from langchain.tools import tool
import re
from typing import List, Dict, Optional, Tuple, Literal
from glob import glob
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from config_file import f_path_out

report_descriptions = {
    "npv": "Contains the Net Present Value (NPV) for each trade, calculated based on discounted future cash flows. The output file, typically 'npv.csv', includes columns such as TradeId (unique trade identifier), NPV (the net present value), and Currency (the currency of the NPV). This report provides a snapshot of trade or portfolio valuation under current market conditions.",
    
    "sensitivity": "Provides sensitivity measures, such as delta and gamma, for specified market risk factors. The primary output file, 'sensitivity.csv', includes columns like TradeId (trade identifier), Factor1 (first risk factor), Factor2 (second risk factor, if applicable), Delta (first-order sensitivity), and Gamma (second-order sensitivity). Additional files, such as 'sensitivity_crossgamma.csv', may detail cross-gamma sensitivities, reflecting interactions between risk factors.",
    
    "stress": "Contains portfolio or trade values under predefined stress scenarios, assessing resilience to extreme market conditions. The output file, typically 'stress.csv', includes columns such as ScenarioId (identifier of the stress scenario), TradeId (trade identifier), and NPV (net present value under the scenario). This report highlights potential vulnerabilities in the portfolio.",
    
    "exposure": "Details exposure metrics over time for counterparty credit risk analysis, such as Expected Positive Exposure (EPE). Outputs are often per-trade or per-netting-set files, like 'exposure_trade_Trade1.csv', with columns including Time (time point in the simulation), Default Value (uncollateralized exposure), Collateral Value (collateral amount), and NPV (net present value). This report supports risk management and collateral optimization.",
    
    "var": "Reports Value at Risk (VaR) for the portfolio, quantifying potential losses over a specified horizon and confidence level. The output file, typically 'var.csv', includes columns such as VaR_95 (VaR at 95% confidence), VaR_99 (VaR at 99% confidence), and Method (calculation method, e.g., historical or parametric). This report aids in understanding portfolio risk exposure.",
    
    "pnl": "Tracks economic profit and loss (P&L) over time, incorporating cash flows and funding costs. The output file, 'pnl.csv', includes columns like Date (valuation date), P&L (profit or loss for the period), CumulativeP&L (running total of P&L), and TradeId (trade identifier). This report monitors financial performance at trade or portfolio levels.",
    
    "hypothetical_pnl": "Generates hypothetical P&L vectors based on historical market movements, used for risk analysis. The output file, 'hypothetical_pnl.csv', includes columns such as ScenarioDate (date of the historical scenario), P&L (profit or loss under the scenario), and TradeId (trade identifier). This report supports stress testing and risk assessment."
}

@tool
def analyze_relevant_files(query: str) -> str:
    """
    Analyze the relevant files based on a user query. Produces a textual response based on the files found.

    Parameters:
    query (str): The user query to be analyzed. The query should be like a question asked to the data to get a specific answer.

    Returns:
    str: The file path of the most relevant file
    """
    # if search_directory is None:
    search_directory = f_path_out
    
    files_list = glob(os.path.join(search_directory, "*.csv"))
    class ChooseFileQuery(BaseModel):
        file_name: Literal[*files_list] = Field(description="The file name to be selected that best describes the query")
        rephrased_query: str = Field(description="Rephrase the user query to make it very objective and specific in terms of the question to be answered by an AI agent to get answer from the data file provided.")
        report_type: Literal[*list(report_descriptions.keys())] = Field(description="The type of report that best describes the query")
   
    
    # Extract key terms from the query
    df_query = llm.with_structured_output(ChooseFileQuery).invoke([SystemMessage(content="You are an expert in finding relevant files based on a user query. Analyze the following query: \n\n"), HumanMessage(content=query)])
    sys_prompt_pandas = f"""You are an expert in analyzing
     data and providing insights by analyzing files using python and pandas library.
     The file provided to you is a {df_query.report_type} report.
     This data contained in this report is described as follows: \n\n{report_descriptions[df_query.report_type]}\n\n
     Analyze the following query: \n\n"""

    analysis_agent_summarizer_prompt_content = """
    You are risk analyst who excels in creating report on the steps that were followed by an agent to come up with final analysis.
    You have to summarize the following text into a report like response in markdown format.
    The text provided is a log of an AI react agent with query thought and action chain.
    You should only summarize the steps followed so that the user can understand what has been done to come up with final analysis.
    Write the report in tone that looks like this: "Step X was performed for getting minimum exposure for given trade." don't use "I performed step X to get minimum ...."
    Make sure the response is in markdown format and in professional tone to summarize all the actions taken to come to final conlusion.
    """
    
    df = pd.read_csv(df_query.file_name)

    agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    prefix=SystemMessage(content=sys_prompt_pandas).content,
    return_intermediate_steps = True,
    agent_type="zero-shot-react-description",
    verbose=False,
    allow_dangerous_code=True,
    handle_parsing_errors=True
    )
    try:
        results = agent_executor.invoke(df_query.rephrased_query)
        sys_prompt = SystemMessage(content=analysis_agent_summarizer_prompt_content)
        plan_to_summarize = 'Analysis Report:\n'+results['output']+'\nSteps followed:\n\n'.join([f'Step {n+1}:\n\n'+i[0].log for n,i in enumerate(results['intermediate_steps'])])
        human_msg = HumanMessage(content=plan_to_summarize)
        results = llm.invoke([sys_prompt]+[human_msg])
        return results.content
    except Exception as e:
        results = llm.invoke([SystemMessage(content="Remove all the error messages from the given text and return just the analysis produced by the llm agent.\n"), HumanMessage(content=str(e))])
        return results.content 

@tool(response_format="content_and_artifact")
def analyze_and_plot_relevant_files(query: str) -> Tuple[str, List[str]]:
    """
    Analyze the relevant files based on a user query, generate a plot based on the query and save it.

    Parameters:
    query (str): The user query to be analyzed. The query should contain clear instructions of what is to be plotted.

    Returns:
    str: The file path of the saved plot
    List[str]: The file name of the saved plot
    """
    search_directory = f_path_out
    
    files_list = glob(os.path.join(search_directory, "*.csv"))
    class ChooseFileQuery(BaseModel):
        file_name: Literal[*files_list] = Field(description="The file name to be selected that best describes the query")
        rephrased_query: str = Field(description="Rephrase the user query to make it very objective and specific in terms of the question to be answered by an AI agent to get answer from the data file provided. You may also choose to use the given query without modification if you think its already spcific and clear to perform analysis.")
        report_type: Literal[*list(report_descriptions.keys())] = Field(description="The type of report that best describes the query")
   
    class IsPlotSaved(BaseModel):
        plot_created_status: Literal["success", "error"] = Field(description="Status of plot being created and saved. Check if plot created and saved successfully inferred from the code generated by agent.")
        plot_file_name: List[str] = Field(description="The file name of the saved plot. It should be intuitive and self-explanatory based on user query.Always save the plots as jpg.", default=[])
    # Extract key terms from the query
    df_query = llm.with_structured_output(ChooseFileQuery).invoke([SystemMessage(content="You are an expert in finding relevant files based on a user query. Analyze the following query: \n\n"), HumanMessage(content=query)])
    sys_prompt_pandas_prefix = f"""You are an expert in creating plots and visualizing data using matplotlib library and providing insights by analyzing files using python and pandas library.
     The file provided to you is a {df_query.report_type} report.
     This data contained in this report is described as follows: \n\n{report_descriptions[df_query.report_type]}\n\n
     Remember to save the plot in the current working directory as jpg with an intuitive name and return back the plot file name and if the plot was successfully created and saved.Important: DO NOT try to display the plot in markdown instead save it in current directory .Analyze the following query and generate a plot requested by user: \n\n"""

   


    analysis_agent_summarizer_prompt_content = """
    You are risk analyst who excels in creating report on the steps that were followed by an agent to come up with final analysis.
    You have to summarize the following text into a report like response in markdown format.
    The text provided is a log of an AI react agent with query thought and action chain.
    You should only summarize the steps followed so that the user can understand what has been done to come up with final analysis.
    Write the report in tone that looks like this: "Step X was performed for getting minimum exposure for given trade." don't use "I performed step X to get minimum ...."
    Make sure the response is in markdown format and in professional tone to summarize all the actions taken to come to final conlusion.
    """
    
    df = pd.read_csv(df_query.file_name)

    agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    prefix=SystemMessage(content=sys_prompt_pandas_prefix).content,
    return_intermediate_steps = True,
    agent_type="zero-shot-react-description",
    verbose=False,
    allow_dangerous_code=True,
    handle_parsing_errors=True,

    )
    try:
        results = agent_executor.invoke(df_query.rephrased_query)
        results_summary = llm.with_structured_output(IsPlotSaved).invoke([SystemMessage(content="Look at the following response from llm and check if plot was created and saved successfully.\n\n"), HumanMessage(content=results['output'])])
        if results_summary.plot_created_status == "error":
            return "Plot was not created or saved successfully.",[]
        else:
            file_name = results_summary.plot_file_name
            if len(file_name) == 0:
                return "Plot was not created or saved successfully.",[]
            elif len(file_name) !=0:
                for i in file_name:
                    if not os.path.exists(i):
                        return "Plot was not created or saved successfully.",[]
                return f"Plot successfully created and saved with name {','.join(file_name)}", file_name
            else:
                return f"Plot successfully created and saved with name {','.join(file_name)}", file_name
                
           
    except Exception as e:
        return 'There was an error while analyzing the file: \n Try again with rephrased query which is more specific in its ask.'

@tool
def get_list_of_relevant_files() -> List[str]:
    """Returns a list of all results files in the f_path_out directory.
    
    Returns:
        List[str]: A list of paths to all csv files in the f_path_out directory.
    """

    return glob(os.path.join(f_path_out, "*.csv"))

# @tool
# def get_human_help(query: str) -> str:
#     """
#     Get help from a human expert.

#     Args:
#         query (str): The query to be answered.

#     Returns:
#         str: The answer to the query.
#     """
#     human_message = 
#     return llm.invoke([SystemMessage(content="You are a human expert in analyzing files and providing insights. Analyze the following query: \n\n"), HumanMessage(content=query)]).content



list_analysis_tools = [analyze_and_plot_relevant_files, analyze_relevant_files, get_list_of_relevant_files]
list_analysis_tools_description = [i.name+" : "+i.description + '\n\n' for n, i in enumerate(list_analysis_tools)]



    
    

