from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from supervisor_node import make_supervisor_node
from ore_xml_agent import ore_xml_agent_node
from sensitivity_agent import sensitivity_agent_node
from ore_execution_agent import ore_execution_agent_node

llm = ChatAnthropic(
    model="claude-3-5-haiku-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)


main_supervisor_node = make_supervisor_node(llm, ["ore_xml_agent", "sensitivity_agent", "ore_execution_agent"])

main_agent_builder = StateGraph(State)
main_agent_builder.add_node("supervisor", main_supervisor_node)
main_agent_builder.add_node("ore_xml_agent", ore_xml_agent_node)
main_agent_builder.add_node("sensitivity_agent", sensitivity_agent_node)
main_agent_builder.add_node("ore_execution_agent", ore_execution_agent_node)

main_agent_builder.add_edge(START, "supervisor")
main_graph = main_agent_builder.compile()

