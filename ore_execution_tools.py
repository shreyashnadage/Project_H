from ORE import *
import os
from langchain.tools import tool
from typing import List
import xml.etree.ElementTree as ET
from typing import Tuple
import utilities_ore as utilities
from config_file import f_path_in
import sys


@tool
def run_ore() -> str:
    """
    Run the ORE model with the specified file.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        cwd = os.getcwd()
        os.chdir(os.path.dirname(f_path_in))
        sys.path.append('..')
        params = Parameters()
        base_folder = os.path.basename(f_path_in)
        params.fromFile(os.path.join(base_folder, 'ore.xml'))
        ore = OREApp(params, True)
        ore.run()
        os.chdir(cwd)
        reports_str = '\n'.join([str(n)+'. '+i for n,i in enumerate(list(ore.getReportNames()))])
        return f"ORE run completed successfully. It generated following reports:{reports_str}"
    except Exception as e:
        return f"Error executing ORE model: {str(e)}"


list_ore_execution_tools = [run_ore]
list_ore_execution_tools_description = [i.name+" : "+i.description +'\n\n' for n, i in enumerate(list_ore_execution_tools)]




