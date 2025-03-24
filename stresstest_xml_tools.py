from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from typing import Optional, Dict
import os
import xml.etree.ElementTree as ET

@tool
def seek_advice_on_stresstest_xml(root_path: str, query: str) -> str:
    """
    This tool should be used as a last resort when no other tools can be used.
    It can help in giving advice to supervisor if it gets stuck with a task that it thinks can't be accomplished by any other tool.

    Args:
        root_path (str): The absolute path to the stresstest.xml file.
        query (str): The query to be answered.

    Returns:
        str: The answer to the query.
    """
    with open(root_path, "r") as f:
        file_content = f.read()
    
    llm = ChatAnthropic(model="claude-3-5-haiku-latest")
    prompt_str = """You are an agent that assists an operator using Open Risk Engine (ORE) to perform stress testing tasks. 
    Your primary role is to understand the stresstest.xml file, which is a key configuration file for stress testing in ORE.
    The **stresstest.xml** file defines the parameters and scenarios for stress testing financial instruments and portfolios.
    It typically includes sections for scenario definitions, shift parameters, and target variables to be stressed.

    Below is the content of the stresstest.xml file:
    {file_content}

    Based on the stresstest.xml file content and its purpose in ORE, answer the following query:
    {query}

    Response:
    """
    prompt = prompt_str.format(file_content=file_content, query=query)
    response = llm.invoke(prompt)
    return response.content

    from langchain.tools import tool

@tool
def create_stresstest_xml(root_path: str) -> str:
    """
    Creates a new stresstest.xml file with a bare minimum template if it doesn't exist.

    Args:
        root_path (str): The absolute path where stresstest.xml should be created.

    Returns:
        str: Success message or error if file already exists.
    """
    if os.path.exists(root_path):
        return "stresstest.xml already exists at the specified path."
    
    root = ET.Element("StressTest")
    scenarios = ET.SubElement(root, "Scenarios")
    scenario = ET.SubElement(scenarios, "Scenario")
    ET.SubElement(scenario, "Name").text = "BaseScenario"
    ET.SubElement(scenario, "ShiftType").text = "Absolute"
    
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")  # Pretty print with indentation
    tree.write(root_path, encoding="utf-8", xml_declaration=True)
    return "Successfully created stresstest.xml with minimum template."

@tool
def add_stress_scenario(root_path: str, scenario_name: str, shift_type: str, parameters: Dict[str, str]) -> str:
    """
    Adds a new stress scenario to the stresstest.xml file.

    Args:
        root_path (str): The absolute path to the stresstest.xml file.
        scenario_name (str): Name of the new scenario.
        shift_type (str): Type of shift (e.g., Absolute, Relative).
        parameters (Dict[str, str]): Dictionary of parameter names and values.

    Returns:
        str: Confirmation message.
    """
    tree = ET.parse(root_path)
    root = tree.getroot()
    scenarios = root.find("Scenarios")
    if scenarios is None:
        scenarios = ET.SubElement(root, "Scenarios")
    
    scenario = ET.SubElement(scenarios, "Scenario")
    ET.SubElement(scenario, "Name").text = scenario_name
    ET.SubElement(scenario, "ShiftType").text = shift_type
    
    for param_name, param_value in parameters.items():
        ET.SubElement(scenario, param_name).text = param_value
    
    ET.indent(tree, space="  ")
    tree.write(root_path, encoding="utf-8", xml_declaration=True)
    return f"Added scenario '{scenario_name}' to stresstest.xml."

@tool
def remove_stress_scenario(root_path: str, scenario_name: str) -> str:
    """
    Removes a specific stress scenario from the stresstest.xml file.

    Args:
        root_path (str): The absolute path to the stresstest.xml file.
        scenario_name (str): Name of the scenario to remove.

    Returns:
        str: Confirmation message or error if not found.
    """
    tree = ET.parse(root_path)
    root = tree.getroot()
    scenarios = root.find("Scenarios")
    
    if scenarios is None:
        return "No scenarios found in stresstest.xml."
    
    for scenario in scenarios.findall("Scenario"):
        name = scenario.find("Name")
        if name is not None and name.text == scenario_name:
            scenarios.remove(scenario)
            ET.indent(tree, space="  ")
            tree.write(root_path, encoding="utf-8", xml_declaration=True)
            return f"Removed scenario '{scenario_name}' from stresstest.xml."
    
    return f"Scenario '{scenario_name}' not found in stresstest.xml."

@tool
def modify_scenario_parameter(root_path: str, scenario_name: str, parameter_name: str, new_value: str) -> str:
    """
    Modifies a parameter value in a specific scenario.

    Args:
        root_path (str): The absolute path to the stresstest.xml file.
        scenario_name (str): Name of the scenario to modify.
        parameter_name (str): Name of the parameter to change.
        new_value (str): New value for the parameter.

    Returns:
        str: Confirmation message or error if not found.
    """
    tree = ET.parse(root_path)
    root = tree.getroot()
    scenarios = root.find("Scenarios")
    
    if scenarios is None:
        return "No scenarios found in stresstest.xml."
    
    for scenario in scenarios.findall("Scenario"):
        name = scenario.find("Name")
        if name is not None and name.text == scenario_name:
            param = scenario.find(parameter_name)
            if param is not None:
                param.text = new_value
                ET.indent(tree, space="  ")
                tree.write(root_path, encoding="utf-8", xml_declaration=True)
                return f"Modified {parameter_name} in scenario '{scenario_name}' to '{new_value}'."
            return f"Parameter '{parameter_name}' not found in scenario '{scenario_name}'."
    
    return f"Scenario '{scenario_name}' not found in stresstest.xml."

@tool
def list_scenarios(root_path: str) -> str:
    """
    Lists all scenarios in the stresstest.xml file.

    Args:
        root_path (str): The absolute path to the stresstest.xml file.

    Returns:
        str: List of scenario names or message if none found.
    """
    tree = ET.parse(root_path)
    root = tree.getroot()
    scenarios = root.find("Scenarios")
    
    if scenarios is None or not scenarios.findall("Scenario"):
        return "No scenarios found in stresstest.xml."
    
    scenario_names = [scenario.find("Name").text for scenario in scenarios.findall("Scenario") 
                     if scenario.find("Name") is not None]
    return "Scenarios found: " + ", ".join(scenario_names)

list_stress_test_tools = [
    create_stresstest_xml,
    add_stress_scenario,
    remove_stress_scenario,
    modify_scenario_parameter,
    list_scenarios
]