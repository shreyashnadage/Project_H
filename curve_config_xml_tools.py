import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool

# Helper function to save XML with proper formatting
def _save_xml(tree: ET.ElementTree, file_path: str) -> None:
    """Save the XML tree to the specified file path with proper indentation."""
    ET.indent(tree, space="  ")  # Pretty print with 2-space indentation
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

# Tool 1: Create a new curveconfig.xml file with a minimal template
@tool
def create_curveconfig_file(file_path: str) -> Dict[str, str]:
    """
    Creates a new curveconfig.xml file with a bare-minimum template if it doesn't exist.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
    
    Returns:
        Dict[str, str]: Status message indicating success or if the file already exists.
    """
    if os.path.exists(file_path):
        return {"status": "File already exists", "path": file_path}
    
    root = ET.Element("CurveConfiguration")
    tree = ET.ElementTree(root)
    _save_xml(tree, file_path)
    return {"status": "New curveconfig.xml created", "path": file_path}

# Tool 2: Add a new curve configuration
@tool
def add_curve_configuration(file_path: str, curve_type: str, curve_data: Dict[str, str]) -> Dict[str, str]:
    """
    Adds a new curve configuration (e.g., SwaptionVolatility, FXVolatility) to the XML file.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
        curve_type (str): Type of curve (e.g., 'SwaptionVolatilities', 'FXVolatility').
        curve_data (Dict[str, str]): Dictionary containing curve configuration details.
    
    Returns:
        Dict[str, str]: Status message indicating success or failure.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "path": file_path}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Ensure the parent element exists (e.g., <SwaptionVolatilities>)
    parent = root.find(curve_type)
    if parent is None:
        parent = ET.SubElement(root, curve_type)
    
    # Create the specific curve element (e.g., <SwaptionVolatility>)
    curve_element_name = curve_type.rstrip('s')  # e.g., 'SwaptionVolatility'
    curve = ET.SubElement(parent, curve_element_name)
    
    # Add curve data as sub-elements
    for key, value in curve_data.items():
        ET.SubElement(curve, key).text = value
    
    _save_xml(tree, file_path)
    return {"status": f"Added {curve_type} configuration", "curve_id": curve_data.get("CurveId", "Unknown")}

# Tool 3: Modify an existing curve configuration
@tool
def modify_curve_configuration(file_path: str, curve_type: str, curve_id: str, updates: Dict[str, str]) -> Dict[str, str]:
    """
    Modifies an existing curve configuration based on its CurveId.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
        curve_type (str): Type of curve (e.g., 'SwaptionVolatilities', 'FXVolatility').
        curve_id (str): Unique identifier of the curve to modify.
        updates (Dict[str, str]): Dictionary of fields to update.
    
    Returns:
        Dict[str, str]: Status message indicating success or failure.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "path": file_path}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Find the specific curve
    curve_element_name = curve_type.rstrip('s')
    curve = root.find(f".//{curve_element_name}[CurveId='{curve_id}']")
    if curve is None:
        return {"status": f"No {curve_type} found with CurveId '{curve_id}'"}
    
    # Update the fields
    for key, value in updates.items():
        element = curve.find(key)
        if element is not None:
            element.text = value
        else:
            ET.SubElement(curve, key).text = value
    
    _save_xml(tree, file_path)
    return {"status": f"Modified {curve_type} with CurveId '{curve_id}'"}

# Tool 4: Delete a curve configuration
@tool
def delete_curve_configuration(file_path: str, curve_type: str, curve_id: str) -> Dict[str, str]:
    """
    Deletes a curve configuration based on its CurveId.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
        curve_type (str): Type of curve (e.g., 'SwaptionVolatilities', 'FXVolatility').
        curve_id (str): Unique identifier of the curve to delete.
    
    Returns:
        Dict[str, str]: Status message indicating success or failure.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "path": file_path}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Find the specific curve
    curve_element_name = curve_type.rstrip('s')
    curve = root.find(f".//{curve_element_name}[CurveId='{curve_id}']")
    if curve is None:
        return {"status": f"No {curve_type} found with CurveId '{curve_id}'"}
    
    # Remove the curve from its parent
    parent = root.find(f".//{curve_element_name}[CurveId='{curve_id}']/..")
    parent.remove(curve)
    
    _save_xml(tree, file_path)
    return {"status": f"Deleted {curve_type} with CurveId '{curve_id}'"}

# Tool 5: Retrieve details of a curve configuration
@tool
def get_curve_configuration(file_path: str, curve_type: str, curve_id: str) -> Dict[str, str]:
    """
    Retrieves details of a specific curve configuration based on its CurveId.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
        curve_type (str): Type of curve (e.g., 'SwaptionVolatilities', 'FXVolatility').
        curve_id (str): Unique identifier of the curve to retrieve.
    
    Returns:
        Dict[str, str]: Dictionary containing the curve configuration details.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "path": file_path}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Find the specific curve
    curve_element_name = curve_type.rstrip('s')
    curve = root.find(f".//{curve_element_name}[CurveId='{curve_id}']")
    if curve is None:
        return {"status": f"No {curve_type} found with CurveId '{curve_id}'"}
    
    # Extract all sub-elements
    curve_data = {child.tag: child.text for child in curve if child.text is not None}
    return {"status": "Success", "curve_data": curve_data}

# Tool 6: Validate the XML structure
@tool
def validate_curveconfig(file_path: str) -> Dict[str, str]:
    """
    Validates the XML structure to ensure required fields are present for each curve type.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
    
    Returns:
        Dict[str, str]: Validation result (success or list of errors).
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "path": file_path}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    errors = []
    required_fields = {
        "SwaptionVolatility": ["CurveId", "Dimension", "VolatilityType"],
        "FXVolatility": ["CurveId", "Dimension"],
        # Add more curve types and their required fields as needed
    }
    
    for curve_type, fields in required_fields.items():
        curve_element_name = curve_type
        for curve in root.findall(f".//{curve_element_name}"):
            for field in fields:
                if curve.find(field) is None:
                    curve_id = curve.find("CurveId").text if curve.find("CurveId") is not None else "Unknown"
                    errors.append(f"Missing '{field}' in {curve_type} with CurveId '{curve_id}'")
    
    if errors:
        return {"status": "Validation failed", "errors": "; ".join(errors)}
    return {"status": "Validation successful"}

# Tool 7: List all curve configurations
@tool
def list_curve_configurations(file_path: str) -> Dict[str, List[str]]:
    """
    Lists all curve configurations in the XML file.
    
    Args:
        file_path (str): Absolute path to the curveconfig.xml file.
    
    Returns:
        Dict[str, List[str]]: Dictionary with curve types and their CurveIds.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "path": file_path}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    curve_types = {}
    for elem in root:
        curve_type = elem.tag
        curve_ids = [curve.find("CurveId").text for curve in elem if curve.find("CurveId") is not None]
        if curve_ids:
            curve_types[curve_type] = curve_ids
    
    return {"status": "Success", "curve_types": curve_types}

@tool
def seek_advice_on_curveconfig_xml(file_path: str, query: str) -> str:
    """
    This tool should be used as a last resort when no other tools can be used.
    It provides advice to the supervisor or operator if the agent gets stuck with a task 
    related to curveconfig.xml that it believes cannot be accomplished by other tools.

    Args:
        file_path (str): The absolute path to the curveconfig.xml file.
        query (str): The query to be answered.

    Returns:
        str: The answer to the query provided by the LLM.
    """
    if not os.path.exists(file_path):
        return "Error: The curveconfig.xml file does not exist at the specified path."

    # Read the curveconfig.xml file content
    with open(file_path, "r") as f:
        file_content = f.read()

    # Initialize the LLM (using Anthropic's Claude as per your example)
    llm = ChatAnthropic(model="claude-3-5-haiku-latest")

    # Updated prompt tailored to curveconfig.xml
    prompt_str = """You are an expert agent assisting an operator who uses the Open Risk Engine (ORE) to manage financial curve configurations. 
    Your primary role is to understand the **curveconfig.xml** file, which is a critical configuration file in ORE used to define various term structures and market objects required to price a portfolio. The file content is provided below, and your task is to provide informed responses based on this content and the operator's query.

    The **curveconfig.xml** file configures:
    - Yield curves, default curves, inflation curves, equity forward price curves, swaption volatility structures, cap/floor volatility structures, FX option volatility structures, CDS volatility structures, inflation cap/floor price surfaces, equity volatility structures, security spreads and recovery rates, base correlation curves, and correlation term structures.
    - Additional market objects such as FXSpots, Security Spreads, and Security Rates necessary for market construction.

    Below is the content of the curveconfig.xml file:
    {file_content}

    Based on the description and content of the curveconfig.xml file, answer the following query from the operator:
    {query}

    Response:
    """

    # Format the prompt with the file content and query
    prompt = prompt_str.format(file_content=file_content, query=query)

    # Send the prompt to the LLM and get the response
    response = llm.invoke(prompt)
    return response.content


list_curve_config_tools = [
    create_curveconfig_file,
    add_curve_configuration,
    modify_curve_configuration,
    delete_curve_configuration,
    list_curve_configurations,
    seek_advice_on_curveconfig_xml,
    get_curve_configuration,
    validate_curve_configuration
]