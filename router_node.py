from ExtendedStatePlanExecute import PlanExecuteState
from typing import Literal
from langgraph.types import Command
from members_details import members
from summary_node import summary_node


def router_node(state: PlanExecuteState) -> Command[Literal[*list(members.keys()), "__end__"]]:
    """
    An LLM-based router.
    """
    plan_step = state['plan_steps'][0]
    next_agent = plan_step[0]
    next_task = plan_step[1]
    stopping_criteria = plan_step[2]
    if state.get("action") == "FINISH":
        return Command(goto="__end__", update={"action": "FINISH", 'markdown_report':summary_node(state)})
    else:
        return Command(goto=next_agent, update={"next_agent": next_agent, "next_task": next_task, "stopping_criteria": stopping_criteria})