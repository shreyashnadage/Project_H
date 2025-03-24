from langchain.tools import tool
import xml.etree.ElementTree as ET
from typing import Tuple




# @tool(response_format="content_and_artifact")
# def read_xml_file(file_path: str = "ore.xml") -> Tuple[str, ET.Element]:
#     """
#     Read and parse XML file from given file_path.

#     Args:
#         file_path (str): The path to the XML file. Defaults to 'ore.xml'.

#     Returns:
#         Tuple[str, ET.Element]: A tuple containing a string indicating if the file has been read successfully or not, and the parsed XML root object.
#     """
#     try:
#         tree = ET.parse(file_path)
#         root = tree.getroot()
#         return "File read successfully.", root
#     except ET.ParseError:
#         return "Error parsing XML file.", ET.Element()
#     except FileNotFoundError:
#         return "File not found.", ET.Element()

@tool(response_format="content")
def get_parameter_value(section: str, parameter_name: str, file_path: str = "ore.xml") -> str:
    """
    Retrieve the value of a specific parameter from the specified section in the given XML file.

    Args:
        section (str): The section name, e.g., 'Setup' or 'Markets'.
        parameter_name (str): The name of the parameter to retrieve.
        file_path (str): The path to the XML file. Defaults to 'ore.xml'.

    Returns:
        str: The value of the parameter, or an error message if not found.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        section_elem = root.find(section)
        if section_elem is None:
            return f"Section '{section}' not found."
        param_elem = section_elem.find(f"Parameter[@name='{parameter_name}']")
        if param_elem is not None:
            return param_elem.text
        else:
            return "Parameter not found."
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."

@tool(response_format="content")
def set_parameter_value(root_path: str, section: str, parameter_name: str, new_value: str) -> str:
    """
    Set the value of a specific parameter in the specified section in the given XML file.

    Args:
        root_path (str): The path to the XML file.
        section (str): The section name, e.g., 'Setup' or 'Markets'.
        parameter_name (str): The name of the parameter to set.
        new_value (str): The new value to set for the parameter.
        root (ET.Element): The root element of the parsed XML tree.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        root = ET.parse(root_path).getroot()
        section_elem = root.find(section)
        if section_elem is None:
            return f"Section '{section}' not found."
        param_elem = section_elem.find(f"Parameter[@name='{parameter_name}']")
        if param_elem is not None:
            param_elem.text = new_value
            tree = ET.ElementTree(root)
            tree.write(root_path)
            return f"Parameter '{parameter_name}' in section '{section}' set to '{new_value}'. saved_results to {root_path}"
        else:
            return "Parameter not found."
    except ET.ParseError:
        return "Error parsing XML file."
    except FileNotFoundError:
        return "File not found."


list_tools = [get_parameter_value, set_parameter_value]