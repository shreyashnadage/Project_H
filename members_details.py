from ore_execution_tools import list_ore_tools_description
from sensitivity_xml_tools import list_sensitivity_tools_description
from ore_xml_tools import list_ore_xml_tools_description
from analysis_agent_tools import list_analysis_tools_description


members = {"ore_xml_agent":f"Use this agent for any task related to ore.xml file.It has following tools:\n{''.join(list_ore_xml_tools_description)}",
           "sensitivity_agent":f"Use this agent for any task related to sensitivity.xml file.It has following tools:\n{''.join(list_sensitivity_tools_description)}",
           "ore_execution_agent":f"Use this agent for any task related to ore execution or any ore executable operation.It has following tools:\n{''.join(list_ore_tools_description)}",
           "analysis_agent":f"Use this agent for any task related to analysis. It has following tools:\n{''.join(list_analysis_tools_description)}"}
