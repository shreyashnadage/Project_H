from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from ore_execution_tools import list_ore_tools as ore_exe_tools_list
from react_agent_system_prompts import *
from langgraph.graph import MessagesState
from langgraph.types import Command
from typing import Literal
from config_file import file_location_prompt


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# Function to summarize chat history
def summarize_messages(state):
    messages = state["messages"]

    # Convert messages to a format suitable for summarization
    chat_history = "\n".join(
        f"Human: {msg.content}" if isinstance(msg, HumanMessage) else f"AI: {msg.content}"
        for msg in messages
    )

    summary_prompt = f"Summarize the following conversation:\n\n{chat_history}\n\nSummary: step by step summary of the conversation."

    # Get the summary from the LLM
    summary = llm.invoke(summary_prompt)

    return {"summary": summary}


class State(MessagesState):
    next: str

llm = ChatAnthropic(
    model="claude-3-5-haiku-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)

input_messages = {'messages': [SystemMessage(content=ore_execution_agent_system_prompt_content),SystemMessage(content=file_location_prompt)]}
ore_execution_agent = create_react_agent(llm,
    tools = ore_exe_tools_list,
)

def ore_execution_agent_node(state: State) -> Command[Literal["supervisor"]]:
    messages_list = input_messages["messages"] + state["messages"]
    messages = {'messages': messages_list}
    response = ore_execution_agent.invoke(messages)
    state["messages"] = messages_list + response["messages"]

    return Command(goto="supervisor", update={"messages": [
                HumanMessage(content=response["messages"][-1].content, name="ore_execution_agent")
            ]})


# test = ore_execution_agent.invoke({'messages': [SystemMessage(content=ore_execution_agent_system_prompt_content),SystemMessage(content=file_location_prompt)] + [HumanMessage(content="run ore with ore.xml")]})

# test1 = 0







