from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from react_agent_system_prompts import analysis_agent_system_prompt_content
from langgraph.types import Command
from typing import Literal
from ExtendedStatePlanExecute import AgentResponseSchema, PlanExecuteState
from analysis_agent_tools import list_analysis_tools
from llm_manager import llm
from summary_node import summary_node
from pydantic import BaseModel, Field
from rich.console import Console
from rich.markdown import Markdown




input_messages = {'messages': [SystemMessage(content=analysis_agent_system_prompt_content)]}
analysis_agent = create_react_agent(llm,
    tools = list_analysis_tools,
    response_format=AgentResponseSchema
)

class SummarizeAnalysis(BaseModel):
    summary: str = Field(description="Summary of the analysis in well structured markdown format.")
    
def summarize_analysis(state: PlanExecuteState, analysis_response: str) :
    analysis_query = state["next_task"]
    summary_prompt = f"You are a Quant Copilot analyst. You are given the following analysis response to the query: \n\n{analysis_query}\n\n Following is the analysis from AI agent for the query above" + analysis_response
    response = llm.with_structured_output(SummarizeAnalysis).invoke([HumanMessage(content=summary_prompt)])
    return response.summary

def analysis_agent_node(state: PlanExecuteState) -> Command[Literal["replanner"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = analysis_agent.invoke(messages)
    response_structured = response['structured_response']
    summary = summarize_analysis(state, response_structured.summary)
    console = Console()
    md = Markdown(summary)
    console.print(md)
    return Command(goto="replanner", update={"messages": [
                AIMessage(content=response_structured.summary.strip(), name="analysis_agent")
            ], 'past_steps': [(state["next_agent"], response_structured.summary, response_structured.status)]})


