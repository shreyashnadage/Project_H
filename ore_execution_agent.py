from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from ore_execution_tools import list_ore_tools as ore_exe_tools_list
from react_agent_system_prompts import *
from ExtendedStatePlanExecute import AgentResponseSchema, PlanExecuteState
from llm_manager import llm
from langgraph.types import Command
from typing import Literal

input_messages = {'messages': [SystemMessage(content=ore_execution_agent_system_prompt_content)]}
ore_execution_agent = create_react_agent(llm,
    tools = ore_exe_tools_list,
    response_format=AgentResponseSchema
)

def ore_execution_agent_node(state: PlanExecuteState) -> Command[Literal["replanner"]]:
    messages_list = input_messages["messages"] + [HumanMessage(content=state["next_task"])] + [HumanMessage(content="Stopping criteria: " + state["stopping_criteria"])]
    messages = {'messages': messages_list}
    response = ore_execution_agent.invoke(messages)
    response_structured = response['structured_response']
    return Command(goto="replanner", update={"messages": [
                AIMessage(content=response_structured.summary.strip(), name="ore_execution_agent")
            ], 'past_steps': [(state["next_agent"], response_structured.summary, response_structured.status)]})









