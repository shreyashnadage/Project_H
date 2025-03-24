from langchain.tools import tool
import xml.etree.ElementTree as ET
from typing import Dict, List
from langchain_anthropic import ChatAnthropic
import os


# Helper function to ensure XML is written with proper formatting
def _write_xml(tree: ET.ElementTree, file_path: str) -> None:
    """Writes the XML tree to the specified file with proper indentation."""
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    # Re-read and write to ensure proper formatting (optional for better readability)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)  # Could use xml.dom.minidom for prettier formatting if needed

# Tool 1: Create a bare-minimum todaysmarket.xml file if it doesn’t exist
@tool
def create_todaysmarket_template(file_path: str) -> Dict[str, str]:
    """
    Creates a bare-minimum todaysmarket.xml file if it doesn’t exist.
    Returns a status message.
    """
    if os.path.exists(file_path):
        return {"status": "File already exists", "file_path": file_path}

    root = ET.Element("TodaysMarket")
    tree = ET.ElementTree(root)
    _write_xml(tree, file_path)
    return {"status": "Bare-minimum todaysmarket.xml created", "file_path": file_path}

# Tool 2: Add a new block (e.g., DiscountingCurves, IndexCurves, etc.)
@tool
def add_market_block(file_path: str, block_type: str, block_id: str, data: Dict[str, str]) -> Dict[str, str]:
    """
    Adds a new block (e.g., DiscountingCurves) with a specified ID and data.
    Example data: {"currency": "EUR", "curve": "Yield/EUR/EUR1D"}
    """
    if not os.path.exists(file_path):
        create_todaysmarket_template(file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    # Check if block with same ID already exists
    for block in root.findall(f".//{block_type}[@id='{block_id}']"):
        return {"status": f"{block_type} with ID '{block_id}' already exists", "file_path": file_path}

    # Create new block
    new_block = ET.SubElement(root, block_type, {"id": block_id})
    for key, value in data.items():
        child = ET.SubElement(new_block, block_type[:-1])  # e.g., DiscountingCurve
        child.set(key, value)  # e.g., currency="EUR"
        child.text = value if key != "currency" and key != "name" else None  # Set text if not an attribute

    _write_xml(tree, file_path)
    return {"status": f"Added {block_type} with ID '{block_id}'", "file_path": file_path}

# Tool 3: Update an existing block
@tool
def update_market_block(file_path: str, block_type: str, block_id: str, data: Dict[str, str]) -> Dict[str, str]:
    """
    Updates an existing block with new data.
    Example data: {"currency": "EUR", "curve": "Yield/EUR/EUR1D"}
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "file_path": file_path}

    tree = ET.parse(file_path)
    root = tree.getroot()

    block = root.find(f".//{block_type}[@id='{block_id}']")
    if block is None:
        return {"status": f"{block_type} with ID '{block_id}' not found", "file_path": file_path}

    # Clear existing children and update with new data
    block.clear()
    block.set("id", block_id)
    for key, value in data.items():
        child = ET.SubElement(block, block_type[:-1])
        child.set(key, value)
        child.text = value if key != "currency" and key != "name" else None

    _write_xml(tree, file_path)
    return {"status": f"Updated {block_type} with ID '{block_id}'", "file_path": file_path}

# Tool 4: Remove a block
@tool
def remove_market_block(file_path: str, block_type: str, block_id: str) -> Dict[str, str]:
    """
    Removes a block with the specified type and ID.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "file_path": file_path}

    tree = ET.parse(file_path)
    root = tree.getroot()

    block = root.find(f".//{block_type}[@id='{block_id}']")
    if block is None:
        return {"status": f"{block_type} with ID '{block_id}' not found", "file_path": file_path}

    root.remove(block)
    _write_xml(tree, file_path)
    return {"status": f"Removed {block_type} with ID '{block_id}'", "file_path": file_path}

# Tool 5: Add a market configuration
@tool
def add_market_configuration(file_path: str, config_id: str, discount_curves_id: str) -> Dict[str, str]:
    """
    Adds a new market configuration with a specified ID and DiscountingCurvesId.
    """
    if not os.path.exists(file_path):
        create_todaysmarket_template(file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    for config in root.findall(f".//Configuration[@id='{config_id}']"):
        return {"status": f"Configuration with ID '{config_id}' already exists", "file_path": file_path}

    config = ET.SubElement(root, "Configuration", {"id": config_id})
    discount_id = ET.SubElement(config, "DiscountingCurvesId")
    discount_id.text = discount_curves_id

    _write_xml(tree, file_path)
    return {"status": f"Added Configuration with ID '{config_id}'", "file_path": file_path}

# Tool 6: Query a block’s contents
@tool
def query_market_block(file_path: str, block_type: str, block_id: str) -> Dict[str, any]:
    """
    Queries the contents of a specific block by type and ID.
    Returns the block’s data as a dictionary.
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "file_path": file_path}

    tree = ET.parse(file_path)
    root = tree.getroot()

    block = root.find(f".//{block_type}[@id='{block_id}']")
    if block is None:
        return {"status": f"{block_type} with ID '{block_id}' not found", "file_path": file_path}

    result = {"id": block_id, "data": {}}
    for child in block:
        tag = child.tag
        attrs = child.attrib
        text = child.text.strip() if child.text else None
        result["data"][tag] = {"attributes": attrs, "text": text}

    return {"status": "Success", "block": result}

# Tool 7: Validate the XML structure
@tool
def validate_todaysmarket(file_path: str) -> Dict[str, str]:
    """
    Validates the basic structure of todaysmarket.xml (e.g., root tag exists).
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "file_path": file_path}

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        if root.tag != "TodaysMarket":
            return {"status": "Invalid root tag, expected 'TodaysMarket'", "file_path": file_path}
        return {"status": "Valid todaysmarket.xml structure", "file_path": file_path}
    except ET.ParseError:
        return {"status": "Invalid XML format", "file_path": file_path}

# Tool 8: List all blocks of a given type
@tool
def list_blocks(file_path: str, block_type: str) -> Dict[str, List[str]]:

    """
    Lists all block IDs for a given block type (e.g., 'DiscountingCurves').
    """
    if not os.path.exists(file_path):
        return {"status": "File does not exist", "file_path": file_path, "blocks": []}

    tree = ET.parse(file_path)
    root = tree.getroot()

    blocks = [block.get("id") for block in root.findall(f".//{block_type}")]
    return {"status": "Success", "blocks": blocks, "file_path": file_path}

# Tool 9: Get advise on todaysmarket.xml
@tool(response_format="content")
def seek_advise_on_todaysmarket_xml(root_path: str, query: str) -> str:
    """
    This tool should be used as a last resort when no other tools can be used.
    It can help in giving advise to supervisor if it gets stuck with a task that it thinks can't be accomplished by any other tool.

    Args:
        root_path (str): The absolute path to the todaysmarket.xml file.
        query (str): The query to be answered.

    Returns:
        str: The answer to the query.
    """
    with open(root_path, "r") as f:
        file_content = f.read()
    llm = ChatAnthropic(model="claude-3-5-haiku-latest")
    prompt_str = """You are an expert agent assisting an operator who uses the Open Risk Engine (ORE) to manage financial market configurations. 
    Your primary role is to understand the **todaysmarket.xml** file, which defines the market data universe for ORE simulations, 
    and provide advice based on operator queries. The **todaysmarket.xml** file is a key configuration file that specifies 
    market data blocks such as DiscountingCurves, IndexCurves, YieldCurves, FX spots, volatilities, and more, as shown below. 
    It is referenced in the master **ore.xml** file to initiate an ORE run.

    Below is the current content of the **todaysmarket.xml** file:
    {file_content}

    The file contains various blocks (e.g., DiscountingCurves, SwaptionVolatilities, Configurations) with unique IDs, 
    and each block defines curves, rates, or volatilities used by ORE for pricing and risk analysis. 
    Your task is to interpret this file and provide actionable advice or explanations based on the operator's query.

    Query from the operator:
    "{query}"

    Provide a clear and concise response to the query based on the structure and content of todaysmarket.xml. 
    If the query cannot be directly answered due to missing information or limitations, suggest a reasonable course of action 
    for the operator to resolve the issue.

    Response:
    """
    prompt = prompt_str.format(file_content=file_content, query=query)
    # Send the prompt to the LLM and get the response
    response = llm.invoke(prompt)
    return response.content


list_todaysmarket_tools = [
    add_market_block,
    remove_market_block,
    add_market_configuration,
    query_market_block,
    validate_todaysmarket,
    list_blocks,
    create_todaysmarket_template,
    seek_advise_on_todaysmarket_xml
]