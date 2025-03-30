from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from ExtendedState import State
from typing import Literal
from llm_manager import llm

class Summary(BaseModel):
    summary: str = Field(description="Summary of the tasks performed so far and also past summary. This is to keep track of past actions and thier outcomes and also to provide context to next task. Should be blank if there is no task performed so far, Should be clear and consise eg: 1. <task performed>:<task outcome>, 2. <task performed>:<task outcome>")
    is_completed: Literal["True", "False"] = Field(description="Is the task completed or not. Should be True if the task is completed, False otherwise.")


def summary_node(response: MessagesState, state: State) -> str:
    summary = llm.with_structured_output(Summary).invoke(response["messages"])
    state["summary"] = summary.summary
    state["is_completed"] = summary.is_completed
    response_txt = f"""
    Given task was: {state["next_task"]}
    Stopping criteria was: {state["stopping_criteria"]}
    Summary of tasks performed by {state["next_agent"]}: {state["summary"]}
    Is task completed: {state["is_completed"]}
    """
    return response_txt