from typing import List, Optional, Literal
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages, SystemMessage
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from react_agent_system_prompts import supervisor_system_prompt
from typing_extensions import TypedDict


class State(MessagesState):
    next: str

def make_supervisor_node(llm: BaseChatModel, members: list[str], state: State, sys_prompt: PromptTemplate=supervisor_system_prompt) -> str:
    options = ["FINISH"] + members
    system_prompt = (sys_prompt.format(members=members))

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""

        next: Literal[*options]

    def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto, update={"next": goto})

    return supervisor_node