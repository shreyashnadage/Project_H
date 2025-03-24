import inspect
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
import tools_utility as t_utility
import ore_xml_tools as tools_ore
from react_agent_system_prompts import ore_agent_system_prompt_content

ore_tools_list = [obj for _, obj in inspect.getmembers(tools_ore) if inspect.isfunction(obj)]
utility_tools_list = [obj for _, obj in inspect.getmembers(t_utility) if inspect.isfunction(obj)]
all_tools_list = ore_tools_list + utility_tools_list


agent = create_react_agent(
    ChatAnthropic,
    all_tools_list,
    SystemMessage(content=ore_agent_system_prompt_content)
)

agent.invoke([HumanMessage(content="What is the base currency in the ore.xml file?")])




