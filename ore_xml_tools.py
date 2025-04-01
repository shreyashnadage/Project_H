from langchain.tools import tool
import xml.etree.ElementTree as ET
import ore_analytics_snippets as ore_snippet
from typing import Tuple, List, Literal
from langchain_anthropic import ChatAnthropic
from config_file import f_path_in
import os


@tool(response_format="content_and_artifact")
def list_analytics() -> Tuple[str, List[str]]:
    """
    List all the analytics present in the ore.xml file.

    Returns:
        Tuple[str, List[str]]: A tuple containing a comma-separated string of analytic types and a list of analytic types.
    """
    try:
        root = ET.parse(os.path.join(f_path_in, 'ore.xml')).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found.", []
        analytics = analytics_section.findall("Analytic")
        types = [analytic.get("type") for analytic in analytics if analytic.get("type")]
        return ", ".join(types), types
    except ET.ParseError:
        return "Error parsing XML file.", []

@tool(response_format="content")
def get_analytic_parameters(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())]) -> str:
    """
    Get all parameters for a specific analytic in the ore.xml file.

    Args:
        analytic_type (str): The type of the analytic, e.g., 'npv', 'cashflow'.

    Returns:
        str: A string representation of the parameters and their values.
    """
    try:
        tree = ET.parse(os.path.join(f_path_in, 'ore.xml'))
        root = tree.getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found."
        analytic_elem = analytics_section.find(f"Analytic[@type='{analytic_type}']")
        if analytic_elem is None:
            return f"Analytic '{analytic_type}' not found."
        params = analytic_elem.findall("Parameter")
        param_dict = {param.get("name"): param.text for param in params if param.get("name")}
        return str(param_dict)
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content")
def set_analytic_active(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())], active: str) -> str:
    """
    Set the 'active' parameter of a specific analytic to 'Y' or 'N'.

    Args:
        analytic_type (str): The type of the analytic.
        active (str): 'Y' to activate, 'N' to deactivate.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    if active not in ['Y', 'N']:
        return "Invalid value for active. Must be 'Y' or 'N'."
    try:
        ore_path = os.path.join(f_path_in, 'ore.xml')
        tree = ET.parse(ore_path)
        root = tree.getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found."
        analytic_elem = analytics_section.find(f"Analytic[@type='{analytic_type}']")
        if analytic_elem is None:
            return f"Analytic '{analytic_type}' not found."
        active_param = analytic_elem.find("Parameter[@name='active']")
        if active_param is not None:
            active_param.text = active
        else:
            ET.SubElement(analytic_elem, "Parameter", name="active").text = active
        tree.write(ore_path)
        return f"Analytic '{analytic_type}' set to active='{active}'. saved results to {ore_path}"
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content")
def add_analytic(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())]) -> str:
    """
    Add a new analytic to the ore.xml file with the specified type and 'active' set to 'Y'.

    Args:
        analytic_type (str): The name of the type of the analytic to add.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        ore_path = os.path.join(f_path_in, 'ore.xml')
        tree = ET.parse(ore_path)
        root = tree.getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found."
        if analytics_section.find(f"Analytic[@type='{analytic_type}']") is not None:
            return f"Analytic '{analytic_type}' already exists."
        new_analytic = ore_snippet.ore_analytics.get(analytic_type)
        if new_analytic is None:
            return f"Invalid analytic type: '{analytic_type}'."
        analytics_section.append(ET.fromstring(new_analytic))
        tree.write(ore_path)
        return f"Added new analytic '{analytic_type}' with active='Y'. saved results to {ore_path}"
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."
    
@tool(response_format="content")
def remove_analytic(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())]) -> str:
    """
    Remove a specific analytic from the ore.xml file.

    Args:
        analytic_type (str): The type of the analytic to remove.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        ore_path = os.path.join(f_path_in, 'ore.xml')
        root = ET.parse(ore_path).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found."
        analytic_elem = analytics_section.find(f"Analytic[@type='{analytic_type}']")
        if analytic_elem is not None:
            analytics_section.remove(analytic_elem)
            tree = ET.ElementTree(root)
            tree.write(ore_path)
            return f"Removed analytic '{analytic_type}'. saved results to {ore_path}"
        else:
            return f"Analytic '{analytic_type}' not found."
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content_and_artifact")
def list_active_analytics() -> Tuple[str, List[str]]:
    """
    List all active analytics in the ore.xml file.

    Returns:
        Tuple[str, List[str]]: A tuple containing a comma-separated string of active analytic types and a list of active analytic types.
    """
    try:
        root = ET.parse(os.path.join(f_path_in, 'ore.xml')).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found.", []
        analytics = analytics_section.findall("Analytic")
        active_types = []
        for analytic in analytics:
            analytic_type = analytic.get("type")
            if analytic_type:
                active_param = analytic.find("Parameter[@name='active']")
                if active_param is not None and active_param.text == 'Y':
                    active_types.append(analytic_type)
        return ", ".join(active_types), active_types
    except ET.ParseError:
        return "Error parsing XML file.", []
    except FileNotFoundError:
        return "File not found.", []

@tool(response_format="content")
def seek_advice_on_ore_xml(query: str) -> str:
    """
    Get advice on ore.xml related tasks when other tools are insufficient.

    This tool should be used as a last resort when no other tools can handle the task.

    Args:
        query (str): The query to be answered.

    Returns:
        str: The answer to the query.
    """
    try:
        with open(os.path.join(f_path_in, 'ore.xml'), "r") as f:
            file_content = f.read()
        llm = ChatAnthropic(model="claude-3-5-haiku-latest")
        results = llm.invoke(f"Here is the content of an ore.xml file:\n{file_content}\n\nQuestion: {query}\n\nPlease provide a detailed answer:")
        return results.content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"Error: {str(e)}"


list_ore_tools = [list_analytics, get_analytic_parameters, set_analytic_active, add_analytic, remove_analytic, list_active_analytics, seek_advice_on_ore_xml]

list_ore_xml_tools_description = [str(n+1)+". "+i.description.split("\n\n")[0]+'\n' for n, i in enumerate(list_ore_tools)]
test  = 0