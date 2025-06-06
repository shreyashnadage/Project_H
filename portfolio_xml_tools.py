from langchain.tools import tool
import xml.etree.ElementTree as ET
import os
from typing import Tuple, List, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from react_agent_system_prompts import portfolio_trade_creator_tool_prompt, portfolio_xml_agent_system_prompt_content
from llm_manager import llm, llm_37
from pydantic import BaseModel, Field
from config_file import f_path_trade_docs, f_path_in, f_path_trade_samples
from glob import glob
from langgraph.types import Command, interrupt
from config_file import term_sheet_file




class ExtractTradeType(BaseModel):
    trade_type: Literal[*os.listdir(f_path_trade_docs)] = Field(str, description="Type of trade to be created.")
    

class GetTradeXMLResponse(BaseModel):
    xml_content: str = Field(str, description="Trade XML generated based details extracted from trade type and term sheet.")
    trade_type: Literal[*os.listdir(f_path_trade_docs)] = Field(str, description="Trade type used to generate XML.")
    trade_id: str = Field(str, description="Trade id used for the modified XML.")

class ModifyTradeResponse(BaseModel):
    summary: str = Field(str, description="Summary of the modification made to the trade")
    status: bool = Field(bool, description="Status of the modification operation")

def extract_trade_doc(trade_type:str) -> str:
    with open(os.path.join(f_path_trade_docs, trade_type), 'r') as f:
        trade_doc = f.read().strip()
    return trade_doc

def extract_trade_sample(trade_type:str) -> str:
    trade_samples = [os.path.basename(i) for i in glob(os.path.join(f_path_trade_samples, '*.xml'))]
    class GetTeadeSample(BaseModel):
        trade_samples_list: List[Literal[*trade_samples]] = Field(str, description="Trade samples that closely match the trade type.")
    result = llm.with_structured_output(GetTeadeSample).invoke([HumanMessage(content=f"Trade type: {trade_type}")])
    return '\n\n'.join(result.trade_samples_list)

    
@tool(response_format="content")
def create_trade_from_term_sheet() -> str:
    """
    Create a new trade in the portfolio.xml file from the termsheet.

    This tool can convert a termsheet or trade description into a trade by extracting its details and add it to the portfolio.xml file.
   
    Returns:
        str: Summary of the XML generated based on trade type.
    """
    try:
        term_sheet_data = term_sheet_file.term_sheet_data
        if (term_sheet_data == ''):
            return "Error: Term sheet data is empty"
        
        trade_type = llm.with_structured_output(ExtractTradeType).invoke([SystemMessage(content=portfolio_xml_agent_system_prompt_content), HumanMessage(content=f"\r\n\r\nYou will be given a term sheet of a financial derivative product. Your job is to identify the trade type described in the term sheet: {term_sheet_data}\r\n\r\n")])
        trade_doc = extract_trade_doc(trade_type=trade_type.trade_type)
        trade_samples = extract_trade_sample(trade_type=trade_type.trade_type)
        trade_result = llm_37.invoke([HumanMessage(content=f"You are an expert trader working for a trading desk in a bank who is tasked in extracting data from from a term sheet that describes a financial derivative product. Your job is to create trade xml snippet with a trade id by extracting relevant trade parameters that you find from the term sheet provided and the documentation of representing that trade as xml.\r\nTrade type: {trade_type.trade_type}\r\nTerm sheet: \r\n{term_sheet_data}\r\n\r\nTrade XML documentation: \r\n{trade_doc}\r\n\r\nHere are a few trade XML samples for reference: \r\n{trade_samples}. Now create an trade xml snippet using the data from term sheet and the sample trade xmls provided above. Return the xml.")])
        result = llm.with_structured_output(GetTradeXMLResponse).invoke([HumanMessage(content=f"You are given a data for financial derivative trade. Your job is to extract xml from the data provided and return the xml.\r\n Data:\r\n{trade_result.content}")])
        trade_xml = ET.fromstring(result.xml_content)
        with open(os.path.join(f_path_in, 'portfolio.xml'), 'r') as f:
            file_content = f.read().strip()
        if file_content == "":
            # Create a new portfolio.xml with a single Trade element
            root = ET.Element('Portfolio')
            root.append(trade_xml)
            tree = ET.ElementTree(root)
            tree.write(os.path.join(f_path_in, 'portfolio.xml'), encoding='unicode', xml_declaration=True)
        else:
            tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
            root = tree.getroot()
            root.append(trade_xml)
            tree.write(os.path.join(f_path_in, 'portfolio.xml'), encoding='unicode', xml_declaration=True)
            
        return f"Generated trade following trade xml for {trade_type.trade_type} successfully.\r\n Trade XML: {ET.tostring(trade_xml, encoding='unicode', method='xml')}"
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
        str: Summary of the modification made to the trade
    """
    try:
        tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
        root = tree.getroot()
        
        # Find the trade with the given ID
        trade = root.find(f".//Trade[@id='{trade_id}']")
        if trade is None:
            return f"Error: Trade with ID {trade_id} not found"
        
        
        modified_trade = llm.with_structured_output(GetTradeXMLResponse).invoke([HumanMessage(content=f"Modify trade xml snippet with a trade id that describes the trade uniquely to be inserted in the portfolio.xml file for {trade_id} trade type using documentation provided to you. Mention the trade id for the modified trade in summary of response \n\nTrade snippet to be modified:\n\n {ET.tostring(trade, encoding='unicode', method='xml')}\n\n modification request:\n\n {modification_query}")])
        
            
        trade_xml = ET.fromstring(modified_trade.xml_content)
        root.append(trade_xml)
        
                
        tree.write(os.path.join(f_path_in, 'portfolio.xml'), encoding="utf-8", xml_declaration=True)
        return f"Successfully modified trade with ID {trade_id}\n\n modified xml of trade: \n\n{ET.tostring(trade_xml, encoding='unicode', method='xml')}"
        
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

@tool(response_format="content")
def list_trades() -> str:
    """
    List all trades in the portfolio.xml file.

    Returns:
        str: List of trades in XML format
    """
    try:
        tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
        root = tree.getroot()
        trades = root.findall(".//Trade")
        if not trades:
            return "No trades found in portfolio.xml"
        
        trade_ids = [trade.attrib['id'] for trade in trades]
        return f"Trade IDs: {', '.join(trade_ids)}"
        
    except Exception as e:
        return f"Error: {str(e)}"

@tool(response_format="content")
def select_trades_by_trade_type(trade_type: str) -> str:
    """
    Select trades of a specific type from the portfolio.xml file.

    Args:
        trade_type (str): Type of trade to select

    Returns:
        str: Trades of the specified type in XML format
    """
    try:
        tree = ET.parse(os.path.join(f_path_in, 'portfolio.xml'))
        root = tree.getroot()
        trades = root.findall(f".//TradeType[@type='{trade_type}']")
        if not trades:
            return f"No trades of type {trade_type} found in portfolio.xml"
        
        trade_ids = [trade.attrib['id'] for trade in trades]
        return f"Trade IDs: {', '.join(trade_ids)}"
        
    except Exception as e:
        return f"Error: {str(e)}"

list_portfolio_xml_tools = [get_trade_info, modify_trade, list_trades, create_trade_from_term_sheet]
list_portfolio_xml_tools_description = [i.name+" : "+i.description + '\n\n' for n, i in enumerate(list_portfolio_xml_tools)]
