from langchain.tools import tool
import xml.etree.ElementTree as ET
from typing import Dict, List
import os
from react_agent_system_prompts import stress_config_agent_system_prompt_content, stress_test_scenario_transaltor_tool_prompt, stress_test_scenario_describer_tool_prompt
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from config_file import f_path_in
from llm_manager import llm


class GetXMLResponse(BaseModel):
    content: str = Field(str, description="Content of the XML generated based on scenario described.")
    summary: str = Field(str, description="Summary of the XML generated based on scenario described. Should highlight what change was made and if the task was successful.")

class GetDescriptionofScenarios(BaseModel):
    summary: str = Field(str, description="Summary describing the scenario in the XML queried by user. Summary should be detailed enough based on user query.")


@tool
def translate_to_stress_test_config(user_query: str) -> str:
    """
    Translate scenario description in user query to stress scenarios in stress test configuration file.


    Args:
        user_query (str): User query to be translated.

    Returns:
        str: summary of what was changed in the stress test configuration.
    """
    try:
        if not os.path.isfile(os.path.join(f_path_in, 'stresstest.xml')):
            with open(os.path.join(f_path_in, 'stresstest.xml'), 'w') as f:
                result = llm.with_structured_output(GetXMLResponse).invoke([SystemMessage(content=stress_config_agent_system_prompt_content),SystemMessage(content=stress_test_scenario_transaltor_tool_prompt), HumanMessage(content=f"\n\nCreate an empty stress test configuration xml")])
                f.write(result.content)
            
        else:
            with open(os.path.join(f_path_in, 'stresstest.xml'), 'r') as f:
                file_content = f.read().strip()
                if file_content == "":
                    with open(os.path.join(f_path_in, 'stresstest.xml'), 'w') as f:
                        result = llm.with_structured_output(GetXMLResponse).invoke([SystemMessage(content=stress_config_agent_system_prompt_content), SystemMessage(content=stress_test_scenario_transaltor_tool_prompt), HumanMessage(content=f"\n\nCreate an empty stress test configuration xml")])
                        f.write(result.content)
                    
            tree = ET.parse(os.path.join(f_path_in, 'stresstest.xml'))
            root = tree.getroot()
            file_content = ET.tostring(root, encoding='unicode')
            message_list = [SystemMessage(content=stress_config_agent_system_prompt_content), SystemMessage(content=stress_test_scenario_transaltor_tool_prompt), HumanMessage(content=f"\n\nCreate a stress test configuration for following user query: \n{user_query}\n\n Current stress test configuration is :\n {file_content}")]
            result = llm.with_structured_output(GetXMLResponse).invoke(message_list)
            new_root = ET.fromstring(result.content)
            tree = ET.ElementTree(new_root)
            ET.indent(tree, space="  ")
            tree.write(os.path.join(f_path_in, 'stresstest.xml'), encoding="utf-8", xml_declaration=True)
        return result.summary
    except Exception as e:
        return f"Error: {str(e)}"
   
@tool
def describe_stress_test_config(user_query: str) -> str:
    """
    Describe stress scenarios in stress test configuration based on user query.

    This function takes as input a user query and returns a string describing
    the stress scenarios in the stress test configuration corresponding to the
    user query.

    Args:
        user_query (str): User query to describe stress scenarios.

    Returns:
        str: Summary of the stress scenarios in the stress test configuration.
    """

    try:
        with open(os.path.join(f_path_in, 'stresstest.xml'), 'r') as f:
            file_content = f.read().strip()
            if file_content == "":
                return "The stress test configuration is empty."
        result = llm.with_structured_output(GetDescriptionofScenarios).invoke([SystemMessage(content=stress_config_agent_system_prompt_content), SystemMessage(content=stress_test_scenario_describer_tool_prompt), HumanMessage(content=f"\n\nDescribe the scenario based on user query: \n{user_query}\n\n Current stress test configuration is :\n {file_content}")])
        return result.summary
    except Exception as e:
        return f"Error: {str(e)}"

list_stress_test_tools = [translate_to_stress_test_config, describe_stress_test_config]
list_stress_test_tools_description = [i.name+" : "+i.description +'\n\n' for n, i in enumerate(list_stress_test_tools)]
