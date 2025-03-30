from typing import Literal
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.types import Command
from langchain.prompts import PromptTemplate
from react_agent_system_prompts import supervisor_system_prompt
from ExtendedState import State
from pydantic import BaseModel, Field


def make_supervisor_node(llm: BaseChatModel, members: dict[str, str], state: State, sys_prompt: PromptTemplate=supervisor_system_prompt) -> str:
    options = ["FINISH"] + list(members.keys())
    members_str = '\n'.join([f"{key}: {value}" for key, value in members.items()])
    system_prompt = (sys_prompt.format(members=members_str))

    class Router(BaseModel):
        """Worker to route to next. If no workers needed, route to FINISH."""
        stopping_criteria_current_agent: str = Field(description="Stopping criteria for current agent to be defined based on current task and tools description of the agent.")
        is_completed: Literal["True", "False"] = Field(description="Whether the task is completed or not based on stopping criteria of current task and also past summary", default="False")
        summary: str = Field(description="Summary of the tasks performed so far and also past summary. This is to keep track of past actions and thier outcomes and also to provide context to next task. Should be blank if there is no task performed so far, Should be clear and consise eg: 1. <task performed>:<task outcome>, 2. <task performed>:<task outcome>")

    class Plan(BaseModel):
        next_agent : Literal[*options] = Field(description="Next agent to be called based on current task and tools description of the agent.")
        next_task : str = Field(description="Task to be performed by next agent based on current task and tools description of the agent.")
        stopping_criteria : str = Field(description="Stopping criteria for current agent to be defined based on current task and tools description of the agent.")
    def supervisor_node(state: State) -> Command[Literal[*list(members.keys()), "__end__"]]:
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response_plan = llm.with_structured_output(Plan).invoke(messages)
            
        state["next_agent"] = response_plan.next_agent
        state["next_task"] = response_plan.next_task
        state["stopping_criteria"] = response_plan.stopping_criteria
        if state["next_agent"]=='FINISH':
            sum_txt = [SystemMessage(content="You have summarize following conversation which is a series of HummanMessages where the first message is a user query and following messages are details of tasks performed by react agents. Summarize the messages given to be presented to the user as final summary of all operations:\n\n")]+state['messages']
            summary_final = llm.invoke(sum_txt)
            print(summary_final.content)
            return Command(goto=END, update={"next_agent": state["next_agent"], "next_task": state["next_task"], "stopping_criteria": state["stopping_criteria"]})
        else:
            return Command(goto=state["next_agent"], update={"next_agent": state["next_agent"], "next_task": state["next_task"], "stopping_criteria": state["stopping_criteria"]})

    return supervisor_node