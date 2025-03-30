from ORE import *
from config_file import f_path
import os
from langchain.tools import tool
from typing import List
import xml.etree.ElementTree as ET
from typing import Tuple    
params = Parameters()
ore = OREApp(params, True)

def convert_paths(absolute_path: str) -> str:
    """
    Iterates over each section of the XML, checks if the parameter name ends with 'File'
    or the parameter value ends with '.xml' or '.txt', and replaces the text with
    the absolute path + basename of the existing value.

    Args:
    - absolute_path (str): Absolute path where ore.xml is located.

    Returns:
    - str: Updated XML content as a string.
    """
    
    # Ensure absolute_path has no trailing slash
    absolute_path = os.path.abspath(absolute_path).rstrip(os.sep)

    # Parse XML
    tree = ET.parse(os.path.join(absolute_path, "ore.xml"))
    root = tree.getroot()

    # Iterate over sections
    for section in root:
        for param in section.findall("Parameter"):
            name = param.get("name", "").strip()
            value = param.text.strip() if param.text else ""

            # Check conditions
            if name.endswith("File") or name.endswith("Path") or value.endswith((".xml", ".txt")):
                new_value = os.path.join(absolute_path, os.path.basename(value))
                param.text = new_value  # Update parameter value
    
    tree.write(os.path.join(absolute_path, "ore.xml"))

    # Return modified XML as a string
    return ET.tostring(root, encoding="unicode")

@tool
def run_ore(file_path: str = None) -> str:
    """
    Run the ORE model with the specified file.

    Args:
        file_path (str): The absolute path to the ore.xml file eg D:Project_H\Examples\Example_1\Inputnew\ore.xml. Defaults to 'ore.xml'.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        absolute_path = os.path.dirname(os.path.dirname(file_path))
        cwd = os.getcwd()
        os.chdir(absolute_path)
        params.fromFile(file_path)
        ore = OREApp(params, True)
        ore.run()
        os.chdir(cwd)
        return "ORE run completed successfully."
    except Exception as e:
        return f"Error executing ORE model: {str(e)}"
    

@tool
def get_ore_report_list(file_path: str = None) -> List[str]:
    """
    Get a list of report names from the ORE model.

    Args:
        file_path (str): The absolute path to the ore.xml file eg D:Project_H\Examples\Example_1\Inputnew\ore.xml. Defaults to 'ore.xml'.

    Returns:
        List[str]: A list of report names.
    """
    try:
        absolute_path = os.path.dirname(os.path.dirname(file_path))
        cwd = os.getcwd()
        os.chdir(absolute_path)
        params.fromFile(file_path)
        ore = OREApp(params, True)
        ore.run()
        os.chdir(cwd)
        return list(ore.getReportNames())
    except Exception as e:
        return f"Error getting report list: {str(e)}"

list_ore_tools = [run_ore, get_ore_report_list]
list_ore_tools_description = [str(n+1)+". "+i.description.split("\n\n")[0]+'\n' for n, i in enumerate(list_ore_tools)]


