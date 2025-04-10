from typing import Literal, List, Tuple, Union
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph import END
from langgraph.types import Command
from langchain.prompts import PromptTemplate
from react_agent_system_prompts import supervisor_system_prompt
from ExtendedState import State
from pydantic import BaseModel, Field
from members_details import members
from ExtendedStatePlanExecute import PlanExecuteState
from llm_manager import llm
from summary_node import summary_node

class CreatePlan(BaseModel):
    plan_steps : List[Tuple[Literal[*list(members.keys())], str, str]] = Field(description="Create a step by step plan as list of string with Tuple of agent, task and stopping criteria based on given user query. should return an empty list if all tasks are already accomplished.")

class FinishOrReplan(BaseModel):
    action : Literal["FINISH", "REPLAN"] = Field(description="Return FINISH if you think all the tasks requested by user is accomplished based on status of execution of past steps else return REPLAN.")


def planner_node(state: PlanExecuteState):
    """An LLM-based planner."""
    members_str = '\n'.join([f"**{key}**: \n{value}" for key, value in members.items()])
    system_prompt = (supervisor_system_prompt.format(members_str=members_str))
    messages = [SystemMessage(content=system_prompt), HumanMessage(content="\n\nCreate a plan for following user query: \n"+state["user_query"])]
    response_plan = llm.with_structured_output(CreatePlan).invoke(messages)
    return {"plan_steps": response_plan.plan_steps}
    

def replanner_node(state: PlanExecuteState):
    members_str = '\n'.join([f"{key}: {value}" for key, value in members.items()])
    system_prompt = (supervisor_system_prompt.format(members_str=members_str))
    current_plan = '\n'.join([f"{n+1}. Agent: {i[0]} || Task: {i[1]} || Stopping criteria: {i[2]}" for n, i in enumerate(state["plan_steps"])])
    user_query = state["user_query"]
    past_steps = '\n'.join([f"{n+1}. Agent: {i[0]} || Task summary: {i[1]} || Task completion status: {i[2]}" for n, i in enumerate(state["past_steps"])])

    replan_prompt = f"""
    You are a planner and you are given a plan and a user query and list of past steps taken to accomplish the task based on the user query.
    You need to do following:
    1. Analyse the user query.
    2. Understand the original plan created.
    3. Understand the past steps taken.
    4. If you think the all the steps in the plan are executed successfully based on past steps return FINISH.
    5. If you think there are still some tasks remaining to be executed based on past steps return updated plan.

    The user query is:
    {user_query}
    
    The existing plan was:
    {current_plan}

    The past steps executed so far are:
    {past_steps}
    
    Analyze above information and return:
    Return FINISH if you think the all the tasks requested by user are accomplished based on all past steps and existing plan.
    Return updated plan if you think the tasks requested by user is not accomplished based on all past steps and existing plan.
    Remember: 
    - The updated plan should not consist of the steps that have already been executed in past steps.
    - The updated plan should be made looking at past steps taken and user query and should only return the plan with steps that need to be executed further.
    - If no further steps left to execute return FINISH with empty list for plan steps.
    """
    messages = [
        {"role": "system", "content": system_prompt},
    ] + [HumanMessage(content=replan_prompt)]
    should_continue = llm.with_structured_output(FinishOrReplan).invoke(messages)
    
    if should_continue.action == "FINISH":
        return Command(goto="__end__", update={"action": "FINISH", 'markdown_report':summary_node(state)})
    else:
        response_replan = llm.with_structured_output(CreatePlan).invoke(messages)
        return Command(goto="router", update={"plan_steps": response_replan.plan_steps})
    