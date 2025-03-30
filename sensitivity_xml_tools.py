from langchain.tools import tool
import xml.etree.ElementTree as ET
from typing import Dict, List
from langchain_anthropic import ChatAnthropic
import os

sensitivity_templates = {
    "DiscountCurve": """
    <DiscountCurves>
      <DiscountCurve ccy="CCY">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </DiscountCurve>
    </DiscountCurves>
    """,
    
    "IndexCurve": """
    <IndexCurves>
      <IndexCurve index="INDEX_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </IndexCurve>
    </IndexCurves>
    """,
    
    "YieldCurve": """
    <YieldCurves>
      <YieldCurve name="CURVE_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </YieldCurve>
    </YieldCurves>
    """,
    
    "FxSpot": """
    <FxSpots>
      <FxSpot ccypair="CCY1CCY2">
        <ShiftType>Relative</ShiftType>
        <ShiftSize>0.01</ShiftSize>
      </FxSpot>
    </FxSpots>
    """,
    
    "FxVolatility": """
    <FxVolatilities>
      <FxVolatility ccypair="CCY1CCY2">
        <ShiftType>Relative</ShiftType>
        <ShiftSize>0.01</ShiftSize>
        <ShiftExpiries>1Y</ShiftExpiries>
        <ShiftStrikes/>
      </FxVolatility>
    </FxVolatilities>
    """,
    
    "SwaptionVolatility": """
    <SwaptionVolatilities>
      <SwaptionVolatility ccy="CCY">
        <ShiftType>Relative</ShiftType>
        <ShiftSize>0.01</ShiftSize>
        <ShiftExpiries>1Y</ShiftExpiries>
        <ShiftTerms>1Y</ShiftTerms>
        <ShiftStrikes/>
      </SwaptionVolatility>
    </SwaptionVolatilities>
    """,
    
    "CapFloorVolatility": """
    <CapFloorVolatilities>
      <CapFloorVolatility ccy="CCY">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftExpiries>1Y</ShiftExpiries>
        <ShiftStrikes>0.01</ShiftStrikes>
        <Index>INDEX_NAME</Index>
      </CapFloorVolatility>
    </CapFloorVolatilities>
    """,
    
    "DefaultProbabilityCurve": """
    <DefaultCurves>
      <DefaultCurve name="CURVE_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </DefaultCurve>
    </DefaultCurves>
    """,
    
    "EquitySpot": """
    <EquitySpots>
      <EquitySpot equity="EQUITY_NAME">
        <ShiftType>Relative</ShiftType>
        <ShiftSize>0.01</ShiftSize>
      </EquitySpot>
    </EquitySpots>
    """,
    
    "EquityVolatility": """
    <EquityVolatilities>
      <EquityVolatility equity="EQUITY_NAME">
        <ShiftType>Relative</ShiftType>
        <ShiftSize>0.01</ShiftSize>
        <ShiftExpiries>1Y</ShiftExpiries>
        <ShiftStrikes/>
      </EquityVolatility>
    </EquityVolatilities>
    """,
    
    "ZeroInflationCurve": """
    <ZeroInflationCurves>
      <ZeroInflationCurve index="INDEX_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </ZeroInflationCurve>
    </ZeroInflationCurves>
    """,
    
    "YearOnYearInflationCurve": """
    <YoYInflationCurves>
      <YoYInflationCurve index="INDEX_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </YoYInflationCurve>
    </YoYInflationCurves>
    """,
    
    "CdsVolatility": """
    <CdsVolatilities>
      <CdsVolatility name="CDS_NAME">
        <ShiftType>Relative</ShiftType>
        <ShiftSize>0.01</ShiftSize>
        <ShiftExpiries>1Y</ShiftExpiries>
        <ShiftStrikes/>
      </CdsVolatility>
    </CdsVolatilities>
    """,
    
    "BondCreditSpread": """
    <SecuritySpreads>
      <SecuritySpread security="SECURITY_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.0001</ShiftSize>
      </SecuritySpread>
    </SecuritySpreads>
    """,
    
    "BaseCorrelationCurve": """
    <BaseCorrelationCurves>
      <BaseCorrelationCurve name="CURVE_NAME">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.01</ShiftSize>
        <ShiftTenors>1Y</ShiftTenors>
      </BaseCorrelationCurve>
    </BaseCorrelationCurves>
    """,
    
    "CorrelationTermStructure": """
    <Correlations>
      <Correlation index1="INDEX1" index2="INDEX2">
        <ShiftType>Absolute</ShiftType>
        <ShiftSize>0.01</ShiftSize>
        <ShiftExpiries>1Y</ShiftExpiries>
        <ShiftStrikes>0</ShiftStrikes>
      </Correlation>
    </Correlations>
    """
}


# Helper function to save the XML tree (not exposed as a tool)
def _save_xml(tree: ET.ElementTree, filepath: str) -> None:
    tree.write(filepath, encoding="utf-8", xml_declaration=True)

@tool
def add_market_component(filepath: str, component_type: str, attributes: Dict[str, str], shifts: Dict[str, str]) -> str:
    """
    Adds a new market component (e.g., DiscountCurve, FxSpot) to the sensitivity.xml file.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        component_type: Type of component (e.g., 'DiscountCurve', 'FxSpot', 'SwaptionVolatility')
        attributes: Dictionary of attributes (e.g., {'ccy': 'USD'} or {'ccypair': 'USDEUR'})
        shifts: Dictionary of shift parameters (e.g., {'ShiftType': 'Absolute', 'ShiftSize': '0.0001', 'ShiftTenors': '1Y,2Y'})
    
    Returns:
        Confirmation message or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    component_section = root.find(component_type + 's')  # e.g., DiscountCurves, FxSpots
    
    if component_section is None:
        component_section = ET.SubElement(root, component_type + 's')
    
    new_component = ET.SubElement(component_section, component_type, attributes)
    for key, value in shifts.items():
        ET.SubElement(new_component, key).text = value
    
    _save_xml(tree, filepath)
    return f"Added {component_type} with attributes {attributes} and shifts {shifts} to {filepath}"

@tool
def modify_market_component(filepath: str, component_type: str, identifier: Dict[str, str], new_shifts: Dict[str, str]) -> str:
    """
    Modifies shift parameters of an existing market component.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        component_type: Type of component (e.g., 'DiscountCurve', 'FxSpot')
        identifier: Dictionary to identify the component (e.g., {'ccy': 'EUR'})
        new_shifts: Dictionary of new shift parameters to update (e.g., {'ShiftSize': '0.001'})
    
    Returns:
        Confirmation or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    component_section = root.find(component_type + 's')
    
    if component_section is None:
        return f"Error: No {component_type}s section found in {filepath}"
    
    for component in component_section.findall(component_type):
        if all(component.get(key) == value for key, value in identifier.items()):
            for key, value in new_shifts.items():
                element = component.find(key)
                if element is not None:
                    element.text = value
                else:
                    ET.SubElement(component, key).text = value
            _save_xml(tree, filepath)
            return f"Modified {component_type} with identifier {identifier} in {filepath}"
    
    return f"Error: No matching {component_type} found with identifier {identifier}"

@tool
def delete_market_component(filepath: str, component_type: str, identifier: Dict[str, str]) -> str:
    """
    Deletes a specific market component from the sensitivity.xml file.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        component_type: Type of component (e.g., 'DiscountCurve', 'FxSpot')
        identifier: Dictionary to identify the component (e.g., {'ccy': 'EUR'})
    
    Returns:
        Confirmation or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    component_section = root.find(component_type + 's')
    
    if component_section is None:
        return f"Error: No {component_type}s section found in {filepath}"
    
    for component in component_section.findall(component_type):
        if all(component.get(key) == value for key, value in identifier.items()):
            component_section.remove(component)
            _save_xml(tree, filepath)
            return f"Deleted {component_type} with identifier {identifier} from {filepath}"
    
    return f"Error: No matching {component_type} found with identifier {identifier}"

@tool
def query_market_component(filepath: str, component_type: str, identifier: Dict[str, str]) -> Dict[str, str]:
    """
    Queries and returns details of a specific market component.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        component_type: Type of component (e.g., 'DiscountCurve', 'FxSpot')
        identifier: Dictionary to identify the component (e.g., {'ccy': 'EUR'})
    
    Returns:
        Dictionary of component details or error message
    """
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} does not exist"}
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    component_section = root.find(component_type + 's')
    
    if component_section is None:
        return {"error": f"No {component_type}s section found in {filepath}"}
    
    for component in component_section.findall(component_type):
        if all(component.get(key) == value for key, value in identifier.items()):
            details = component.attrib.copy()
            for elem in component:
                details[elem.tag] = elem.text
            return details
    
    return {"error": f"No matching {component_type} found with identifier {identifier}"}

@tool
def add_cross_gamma_pair(filepath: str, pair: str) -> str:
    """
    Adds a new pair to the CrossGammaFilter section.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        pair: String representing the pair (e.g., 'DiscountCurve/EUR,IndexCurve/EUR')
    
    Returns:
        Confirmation or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    cross_gamma_filter = root.find("CrossGammaFilter")
    
    if cross_gamma_filter is None:
        cross_gamma_filter = ET.SubElement(root, "CrossGammaFilter")
    
    # Check if pair already exists
    for existing_pair in cross_gamma_filter.findall("Pair"):
        if existing_pair.text == pair:
            return f"Pair {pair} already exists in CrossGammaFilter"
    
    ET.SubElement(cross_gamma_filter, "Pair").text = pair
    _save_xml(tree, filepath)
    return f"Added pair {pair} to CrossGammaFilter in {filepath}"

@tool
def delete_cross_gamma_pair(filepath: str, pair: str) -> str:
    """
    Deletes a specific pair from the CrossGammaFilter section.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        pair: String representing the pair to delete (e.g., 'DiscountCurve/EUR,IndexCurve/EUR')
    
    Returns:
        Confirmation or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    cross_gamma_filter = root.find("CrossGammaFilter")
    
    if cross_gamma_filter is None:
        return f"Error: No CrossGammaFilter section found in {filepath}"
    
    for existing_pair in cross_gamma_filter.findall("Pair"):
        if existing_pair.text == pair:
            cross_gamma_filter.remove(existing_pair)
            _save_xml(tree, filepath)
            return f"Deleted pair {pair} from CrossGammaFilter in {filepath}"
    
    return f"Error: Pair {pair} not found in CrossGammaFilter"

@tool
def toggle_compute_gamma(filepath: str, value: bool) -> str:
    """
    Toggles the ComputeGamma flag in the sensitivity.xml file.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        value: Boolean value to set (True or False)
    
    Returns:
        Confirmation or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    compute_gamma = root.find("ComputeGamma")
    
    if compute_gamma is None:
        compute_gamma = ET.SubElement(root, "ComputeGamma")
    
    compute_gamma.text = str(value).lower()
    _save_xml(tree, filepath)
    return f"Set ComputeGamma to {value} in {filepath}"

@tool
def toggle_use_spreaded_term_structures(filepath: str, value: bool) -> str:
    """
    Toggles the UseSpreadedTermStructures flag in the sensitivity.xml file.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        value: Boolean value to set (True or False)
    
    Returns:
        Confirmation or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist."
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    spreaded_term = root.find("UseSpreadedTermStructures")
    
    if spreaded_term is None:
        spreaded_term = ET.SubElement(root, "UseSpreadedTermStructures")
    
    spreaded_term.text = str(value).lower()
    _save_xml(tree, filepath)
    return f"Set UseSpreadedTermStructures to {value} in {filepath}"

@tool
def list_market_components(filepath: str, component_type: str) -> List[Dict[str, str]]:

    """
    Lists all market components of a given type in the sensitivity.xml file.
    
    Args:
        filepath: Absolute path to sensitivity.xml
        component_type: Type of component (e.g., 'DiscountCurve', 'FxSpot')
    
    Returns:
        List of dictionaries containing component details
    """
    if not os.path.exists(filepath):
        return [{"error": f"File {filepath} does not exist"}]
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    component_section = root.find(component_type + 's')
    
    if component_section is None:
        return [{"error": f"No {component_type}s section found in {filepath}"}]
    
    components = []
    for component in component_section.findall(component_type):
        details = component.attrib.copy()
        for elem in component:
            details[elem.tag] = elem.text
        components.append(details)
    
    return components if components else [{"message": f"No {component_type} components found"}]

@tool
def seek_advise_on_sensitivity_xml(root_path: str, query: str) -> str:
    """
    This tool should be used as a last resort when no other tools can be used.
    It can help in giving advise to supervisor if it gets stuck with a task that it thinks can't be accomplished by any other tool.

    Args:
        root_path (str): The absolute path to the sensitivity.xml file.
        query (str): The query to be answered.

    Returns:
        str: The answer to the query.
    """
    with open(root_path, "r") as f:
        file_content = f.read()
    llm = ChatAnthropic(model="claude-3-5-haiku-latest")

    prompt_str = """You are an AI assistant specialized in managing the sensitivity.xml file for ORE (Open Source Risk Engine).
     The sensitivity.xml file is a critical configuration file in ORE that defines how sensitivity analysis is performed on various market components, 
     such as discount curves, FX spots, volatilities, and more. It specifies parameters like shift types (absolute or relative), shift sizes, and 
     tenor/expiry/strike buckets for curves and surfaces, enabling ORE to compute first- and second-order sensitivities (e.g., delta and gamma) for risk analysis.
     The file supports a wide range of financial instruments, including yield curves, swaption volatilities, and cap/floor volatilities, 
     with detailed settings for each component stored in XML sections like DiscountCurves, FxSpots, or CrossGammaFilter. 
     Additional flags like ComputeGamma and UseSpreadedTermStructures control advanced computation options.
     Your role is to interpret, modify, and manage this file based on user queries, ensuring accurate and efficient sensitivity analysis within ORE.
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
def create_new_sensitivity_xml(filepath: str) -> str:
    """
    Creates a new sensitivity.xml file with a bare minimum template structure for ORE.
    
    Args:
        filepath: Absolute path where the new sensitivity.xml file will be saved
    
    Returns:
        Confirmation message or error message
    """
    # Check if file already exists to avoid overwriting
    if os.path.exists(filepath):
        return f"Error: File {filepath} already exists. Please provide a new path or delete the existing file."

    # Create the root element
    root = ET.Element("SensitivityAnalysis")

    # Add placeholder sections for common market components (empty for minimal structure)
    ET.SubElement(root, "DiscountCurves")
    ET.SubElement(root, "IndexCurves")
    ET.SubElement(root, "YieldCurves")
    ET.SubElement(root, "FxSpots")
    ET.SubElement(root, "FxVolatilities")
    ET.SubElement(root, "SwaptionVolatilities")
    ET.SubElement(root, "CapFloorVolatilities")
    ET.SubElement(root, "SecuritySpreads")
    ET.SubElement(root, "Correlations")
    ET.SubElement(root, "CrossGammaFilter")

    # Add mandatory flags with default values
    ET.SubElement(root, "ComputeGamma").text = "true"
    ET.SubElement(root, "UseSpreadedTermStructures").text = "false"

    # Create the ElementTree object and save the file
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)

    return f"Successfully created new sensitivity.xml file at {filepath} with minimal template structure."

@tool
def insert_risk_factor_template(filepath: str, component_type: str) -> str:
    """
    Inserts a risk factor template into the sensitivity.xml file if its section is absent.
    
    Args:
        filepath: Absolute path to the sensitivity.xml file
        component_type: Type of risk factor (e.g., 'DiscountCurve', 'FxSpot')
    
    Returns:
        Confirmation message or error message
    """
    # Validate component_type
    if component_type not in sensitivity_templates:
        return f"Error: Invalid component type '{component_type}'. Supported types: {list(sensitivity_templates.keys())}"
    
    # Check if file exists
    if not os.path.exists(filepath):
        return f"Error: File {filepath} does not exist. Please create it first using create_new_sensitivity_xml."

    # Parse the existing XML file
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Determine the section name (plural form, e.g., DiscountCurves)
    section_name = component_type + "s" if not component_type.endswith("s") else component_type
    
    # Check if the section already exists
    if root.find(section_name) is not None:
        return f"Section '{section_name}' already exists in {filepath}. No changes made."

    # Parse the template and insert it
    template_root = ET.fromstring(sensitivity_templates[component_type])
    root.append(template_root)  # Append the entire section (e.g., <DiscountCurves>)

    # Save the modified XML
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    return f"Inserted '{component_type}' template into {filepath} under '{section_name}' section."


list_sensitivity_tools = [add_market_component, modify_market_component, delete_market_component, query_market_component, toggle_compute_gamma, toggle_use_spreaded_term_structures, list_market_components, seek_advise_on_sensitivity_xml, add_cross_gamma_pair, delete_cross_gamma_pair,insert_risk_factor_template, create_new_sensitivity_xml]
list_sensitivity_tools_description = [str(n+1)+". "+i.description.split("\n\n")[0]+'\n' for n, i in enumerate(list_sensitivity_tools)]







