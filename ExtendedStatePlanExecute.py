from langgraph.graph import MessagesState
from typing import Annotated, List, Tuple, Literal, Optional
from config_file import f_path_in, f_path_out
from operator import add
import os
from members_details import members
from pydantic import BaseModel, Field

class PlanExecuteState(MessagesState):
    plan_steps:  Annotated[Optional[List[Tuple[Literal[*list(members.keys())], str, str]]], "Step by step plan as list of string with task, agent and stopping criteria based on given user query."]
    next_agent:  Annotated[Optional[str], "Next agent to be called based on current task and tools description of the agent."]
    next_task:  Annotated[Optional[str], "Next task to be executed by next agent based on current task and tools description of the agent."]
    stopping_criteria:  Annotated[Optional[str], "Stopping criteria for current agent to be defined based on current task and tools description of the agent."]
    task_status:  Annotated[Optional[Literal["True", "False"]], "Is the task completed or not. Should be True if the task is completed, False otherwise."]
    input_path:  Annotated[str, "Input path for the setup require to run ORE"] 
    output_path:  Annotated[str, "Output path for results of ORE are generated"] 
    user_query:  Annotated[str, "User query from which the plan is generated"]
    past_steps:  Annotated[Optional[List[Tuple[str, str, Literal["True", "False"]]]], "Agent response to the given task as tuple of task, summary response of agent and task status", add]
    action:  Annotated[Optional[Literal["FINISH"]], "Action to be taken based on current task and tools description of the agent."]

class AgentResponseSchema(BaseModel):
    task: str
    summary: str
    status: Literal["True", "False"]
