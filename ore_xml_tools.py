from langchain.tools import tool
import xml.etree.ElementTree as ET
import ore_analytics_snippets as ore_snippet
from typing import Tuple, List, Literal
from langchain_anthropic import ChatAnthropic



@tool(response_format="content")
def list_analytics(root_path: str = None) -> Tuple[str, List[str]]:
    """
    List all the analytics present in the ore.xml file.

    Args:
        root_path (str): The absolute path to the ore.xml file. Defaults to 'ore.xml'.

    Returns:
        Tuple[str, List[str]]: A tuple containing a comma-separated string of analytic types and a list of analytic types.
    """
    try:
        root = ET.parse(root_path).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found.", []
        analytics = analytics_section.findall("Analytic")
        types = [analytic.get("type") for analytic in analytics if analytic.get("type")]
        return ", ".join(types), types
    except ET.ParseError:
        return "Error parsing XML file.", []

@tool(response_format="content")
def get_analytic_parameters(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())], root_path: str = None) -> str:
    """
    Get all parameters for a specific analytic in the ore.xml file.

    Args:
        analytic_type (str): The type of the analytic, e.g., 'npv', 'cashflow'.
        root_path (str): The absolute path to the ore.xml file. Defaults to 'ore.xml'.

    Returns:
        str: A string representation of the parameters and their values.
    """
    try:
        tree = ET.parse(root_path)
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
def set_analytic_active(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())], active: str, root_path: str = None) -> str:
    """
    Set the 'active' parameter of a specific analytic to 'Y' or 'N'.

    Args:
        analytic_type (str): The type of the analytic.
        active (str): 'Y' to activate, 'N' to deactivate.
        root_path (str): The absolute path to the ore.xml file. Defaults to 'ore.xml'.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    if active not in ['Y', 'N']:
        return "Invalid value for active. Must be 'Y' or 'N'."
    try:
        tree = ET.parse(root_path)
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
        tree.write(root_path)
        return f"Analytic '{analytic_type}' set to active='{active}'. saved results to {root_path}"
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content")
def add_analytic(analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())], root_path: str = None) -> str:
    """
    Add a new analytic to the ore.xml file with the specified type and 'active' set to 'Y'.

    Args:
        analytic_type (str): The name of the type of the analytic to add.
        root_path (str): The absolute path to the ore.xml file. Defaults to 'ore.xml'.

    Returns:
        str: A confirmation message indicating success or failure.
        ET.Element: The root element of the parsed XML tree.
    """
    try:
        tree = ET.parse(root_path)
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
        tree.write(root_path)
        return f"Added new analytic '{analytic_type}' with active='Y'. saved results to {root_path}"
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."
    
@tool(response_format="content")
def set_analytic_parameter(root_path:str, analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())], parameter_name: str, value: str) -> str:
    """
    Set the value of a specific parameter for a given analytic in the ore.xml file.

    Args:
        root_path (str): The absolute path to the ore.xml file.
        analytic_type (str): The type of the analytic.
        parameter_name (str): The name of the parameter to set.
        value (str): The value to set for the parameter.
        root (ET.Element): The root element of the parsed XML tree.

    Returns:
        str: A confirmation message indicating success or failure.
        ET.Element: The root element of the parsed XML tree.
    """
    try:
        root = ET.parse(root_path).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found.", root
        analytic_elem = analytics_section.find(f"Analytic[@type='{analytic_type}']")
        if analytic_elem is None:
            return f"Analytic '{analytic_type}' not found."
        param_elem = analytic_elem.find(f"Parameter[@name='{parameter_name}']")
        if param_elem is not None:
            param_elem.text = value
        else:
            ET.SubElement(analytic_elem, "Parameter", name=parameter_name).text = value
        tree = ET.ElementTree(root)
        tree.write(root_path)
        return f"Set parameter '{parameter_name}' to '{value}' for analytic '{analytic_type}'. saved results to {root_path}"
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content")
def remove_analytic(root_path: str, analytic_type: Literal[*list(ore_snippet.ore_analytics.keys())]) -> str:
    """
    Remove a specific analytic from the ore.xml file.

    Args:
        root_path (str): The absolute path to the ore.xml file.
        analytic_type (str): The type of the analytic to remove.
        root (ET.Element): The root element of the parsed XML tree.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        root = ET.parse(root_path).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found."
        analytic_elem = analytics_section.find(f"Analytic[@type='{analytic_type}']")
        if analytic_elem is not None:
            analytics_section.remove(analytic_elem)
            tree = ET.ElementTree(root)
            tree.write(root_path)
            return f"Removed analytic '{analytic_type}'. saved results to {root_path}"
        else:
            return f"Analytic '{analytic_type}' not found."
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content_and_artifact")
def list_active_analytics(root_path: str) -> Tuple[str, List[str]]:
    """
    List all active analytics in the ore.xml file.

    Args:
        root_path (str): The absolute path to the ore.xml file.

    Returns:
        Tuple[str, List[str]]: A tuple containing a comma-separated list of active analytic types and the list of active analytics.
    """
    try:
        root = ET.parse(root_path).getroot()
        analytics_section = root.find("Analytics")
        if analytics_section is None:
            return "Analytics section not found.", []
        active_analytics = []
        for analytic in analytics_section.findall("Analytic"):
            active_param = analytic.find("Parameter[@name='active']")
            if active_param is not None and active_param.text == "Y":
                active_analytics.append(analytic.get("type"))
        return ", ".join(active_analytics), active_analytics
    except ET.ParseError:
        return "Error parsing XML file."

@tool(response_format="content")
def seek_advise_on_ore_xml(root_path: str, query: str) -> str:
    """
    This tool should be used as a last resort when no other tools can be used.
    It can help in giving advise to supervisor if it gets stuck with a task that it thinks can't be accomplished by any other tool.

    Args:
        root_path (str): The absolute path to the ore.xml file.
        query (str): The query to be answered.

    Returns:
        str: The answer to the query.
    """
    with open(root_path, "r") as f:
        file_content = f.read()
    llm = ChatAnthropic(model="claude-3-5-haiku-latest")
    prompt_str = """You are an agent that helps an operator who uses Open risk engine (ORE) to perform given tasks. 
    Your main job is to understand ore.xml file which is described below and provide response based on queries from operator. 
    The **ore.xml** file is the **master input file** that initiates a run of ORE. It is given as a single command line parameter to the ORE executable. This file serves as the **starting point for the engine's configuration**.
    below is the description of ore.xml file in tex format:
    {file_content}
    

    Based on the description of ore.xml file, answer the following query:
    {query}

    Response:
    """
    prompt = prompt_str.format(file_content=file_content, query=query)
    # Send the prompt to the LLM and get the response
    response = llm.invoke(prompt)
    return response.content


@tool
def ask_human(query: str) -> str:
    """
    This tool should be used as a last resort when no other tools can be used.
    It can help in giving advise to supervisor if it gets stuck with a task that it thinks can't be accomplished by any other tool.

    Args:
        query (str): The query to be answered.

    Returns:
        str: The answer to the query.
    """
    return query
list_ore_tools = [list_analytics, get_analytic_parameters, set_analytic_active, add_analytic, set_analytic_parameter, remove_analytic, list_active_analytics, seek_advise_on_ore_xml]
