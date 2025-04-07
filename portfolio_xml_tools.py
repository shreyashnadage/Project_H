from langchain.tools import tool
import xml.etree.ElementTree as ET
import os
from typing import Tuple, List, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from react_agent_system_prompts import portfolio_trade_creator_tool_prompt, portfolio_xml_agent_system_prompt_content
from llm_manager import llm
from pydantic import BaseModel, Field
from config_file import f_path_trade_docs, f_path_in





class ExtractTradeType(BaseModel):
    trade_type: Literal[*os.listdir(f_path_trade_docs)] = Field(str, description="Type of trade to be created.")
    

class GetTradeXMLResponse(BaseModel):
    xml_content: str = Field(str, description="Content of the XML generated based on trade type.")
    trade_type: Literal[*os.listdir(f_path_trade_docs)] = Field(str, description="Trade type used to generate XML.")

class ModifyTradeResponse(BaseModel):
    summary: str = Field(str, description="Summary of the modification made to the trade")
    status: bool = Field(bool, description="Status of the modification operation")

def extract_trade_doc(trade_type:str) -> HumanMessage:
    with open(os.path.join(f_path_trade_docs, trade_type), 'r') as f:
        trade_doc = f.read().strip()
    portfolio_trade_creator_tool_prompt_sys = portfolio_trade_creator_tool_prompt.format(tex_doc=trade_doc)
    return SystemMessage(content=portfolio_trade_creator_tool_prompt_sys)
    
@tool(response_format="content")
def create_trade(user_query: str) -> str:
    """
    Create a new trade in the portfolio.xml file.

    This function takes as input a user query and returns a string containing the XML code for the new trade.

    Args:
        user_query (str): User query to be translated.

    Returns:
        str: Summary of the XML generated based on trade type.
    """
    try:
        with open(os.path.join(f_path_in, 'portfolio.xml'), 'r') as f:
            file_content = f.read().strip()
            if file_content == "":
                return "The portfolio.xml file is empty."
            else:
                tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
                root = tree.getroot()

                trade_type = llm.with_structured_output(ExtractTradeType).invoke([SystemMessage(content=portfolio_xml_agent_system_prompt_content), HumanMessage(content=f"\n\nUser Query: {user_query}\n\n")])
                trade_doc = extract_trade_doc(trade_type=trade_type.trade_type)
                result = llm.with_structured_output(GetTradeXMLResponse).invoke([trade_doc, HumanMessage(content=f"\n\nCreate trade xml snippet with a trade id that describes the trade uniquely to be inserted in the portfolio.xml file for  {trade_type.trade_type} trade type using documentation provided to you. Mention the trade id for the created trade in summary of response \n\n")])
                trade_xml = ET.fromstring(result.xml_content)
                root.append(trade_xml)
                tree.write(os.path.join(f_path_in, 'portfolio.xml'), encoding="utf-8", xml_declaration=True)
        return f"Generated trade following trade xml for {trade_type.trade_type} successfully.\n\n Trade ID: {trade_xml.find('Trade').attrib['id']} "
    except Exception as e:
        return f"Error: {str(e)}"


@tool(response_format="content")
def modify_trade(trade_id: str, modification_query: str) -> str:
    """
    Modify an existing trade in the portfolio.xml file.

    Args:
        trade_id (str): ID of the trade to modify
        modification_query (str): Query describing the modification to be made

    Returns:
        str: Summary of the modification made
    """
    try:
        tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
        root = tree.getroot()
        
        # Find the trade with the given ID
        trade = root.find(f".//Trade[@id='{trade_id}']")
        if trade is None:
            return f"Error: Trade with ID {trade_id} not found"
            
        # Parse the modification query and update the trade
        if "delete" in modification_query.lower():
            root.remove(trade)
            tree.write(os.path.join(f_path_in, 'portfolio.xml'), encoding="utf-8", xml_declaration=True)
            return f"Successfully deleted trade with ID {trade_id}"
            
        # For parameter modifications
        for param in trade.findall(".//Parameter"):
            param_name = param.get('name')
            if param_name.lower() in modification_query.lower():
                # Extract new value from query using LLM
                new_value = llm.invoke(f"Extract the new value for parameter {param_name} from: {modification_query}")
                param.set('value', new_value.strip())
                
        tree.write(os.path.join(f_path_in, 'portfolio.xml'), encoding="utf-8", xml_declaration=True)
        return f"Successfully modified trade with ID {trade_id}"
        
    except Exception as e:
        return f"Error: {str(e)}"

@tool(response_format="content")
def get_trade_info(trade_id: str) -> str:
    """
    Get information about a specific trade.

    Args:
        trade_id (str): ID of the trade to retrieve

    Returns:
        str: Trade information in XML format
    """
    try:
        tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
        root = tree.getroot()
        
        trade = root.find(f".//Trade[@id='{trade_id}']")
        if trade is None:
            return f"Error: Trade with ID {trade_id} not found"
            
        return ET.tostring(trade, encoding='unicode', method='xml')
        
    except Exception as e:
        return f"Error: {str(e)}"

list_portfolio_xml_tools = [create_trade, get_trade_info, modify_trade]
list_portfolio_xml_tools_description = [str(n+1)+". "+i.description.split("\n\n")[0]+'\n' for n, i in enumerate(list_portfolio_xml_tools)]
