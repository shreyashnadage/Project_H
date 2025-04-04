from ORE import *
import os
from langchain.tools import tool
from typing import List
import xml.etree.ElementTree as ET
from typing import Tuple
from config_file import f_path_in
params = Parameters()

params.fromFile(os.path.join(f_path_in, 'ore.xml'))

ore = OREApp(params, True)


@tool
def run_ore() -> str:
    """
    Run the ORE model with the specified file.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        cwd = os.getcwd()
        os.chdir(os.path.join(f_path_in, '..'))
        ore.run()
        os.chdir(cwd)
        return "ORE run completed successfully."
    except Exception as e:
        return f"Error executing ORE model: {str(e)}"


@tool
def get_ore_report_list() -> List[str]:
    """
    Get a list of report names from the ORE model.

    Returns:
        List[str]: A list of report names.
    """
    try:
        cwd = os.getcwd()
        os.chdir(os.path.join(f_path_in, '..'))
        ore.run()
        os.chdir(cwd)
        return list(ore.getReportNames())
    except Exception as e:
        return f"Error getting report list: {str(e)}"


list_ore_tools = [run_ore, get_ore_report_list]
list_ore_tools_description = [str(n+1)+". "+i.description.split("\n\n")[0]+'\n' for n, i in enumerate(list_ore_tools)]


