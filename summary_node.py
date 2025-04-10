from pydantic import BaseModel, Field
from ExtendedStatePlanExecute import PlanExecuteState
from langchain_core.messages import HumanMessage
from typing import Literal
from rich.console import Console
from rich.markdown import Markdown
from llm_manager import llm

class Summary(BaseModel):
    summary: str = Field(description="Summary of the tasks performed so far and also past summary. This is to keep track of past actions and thier outcomes and also to provide context to next task. Should be blank if there is no task performed so far, Should be clear and consise eg: 1. <task performed>:<task outcome>, 2. <task performed>:<task outcome>")
    is_completed: Literal["True", "False"] = Field(description="Is the task completed or not. Should be True if the task is completed, False otherwise.")


def summary_node(state: PlanExecuteState) -> str:
    
    

    summary_response = f"""
    You are a copilot to a quant working in investement bank. You have successfully completed the task requested by user.
    You will be given the user query and the steps taken by the AI agent so far to accomplish the task.
    Your job is: 
    1. Understand the user query.
    2. Understand the steps taken by the AI agent which will be in form of list of tuple of (agent, task, task completion status).
    3. Summarize the steps taken by the AI agent.
    4. Return the summary in well formatted markdown report that looks professional.

    User query is:
    {state['user_query']}
    
    Steps taken by the AI agent are:
    {state['past_steps']}

    Dump of messages are:
    {state['messages']}
    
    Return the summary in well formatted markdown report that looks professional.
    The report should consist of following:
    - Describe the user query.
    - List of steps taken by the AI agent.
    - Summary of the tasks performed so far.
    - mention the name of author as: QuantCatalyst Copilot.
    """
    summary = llm.invoke([HumanMessage(content=summary_response)])
    return summary.content
