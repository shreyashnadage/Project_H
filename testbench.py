# from langchain_community.document_loaders import PyPDFLoader
# from portfolio_xml_tools import create_trade_from_term_sheet


# loader = PyPDFLoader(r'D:\Project_H\usd-inr-ccs-fixed-float.pdf')
# pages = []
# doc_data = ''
# for page in loader.lazy_load():
#     pages.append(page)
#     doc_data += page.page_content + '\n'
# test = create_trade_from_term_sheet.invoke({"user_query": "Create a trade from given term sheet data.", "term_sheet_data": doc_data})

from langgraph.types import interrupt
from langgraph.graph import MessagesState

def main_node(state:State):
    state["some_text"] = "Ram"
    return {"some_text": state["some_text"]}

class State(MessageState):
    some_text: str = ""

def human_node(state: State):
    value = interrupt(
        # Any JSON serializable value to surface to the human.
        # For example, a question or a piece of text or a set of keys in the state
       {
          "text_to_revise": state["some_text"]
       }
    )
    # Update the state with the human's input or route the graph based on the input.
    return {
        "some_text": value
    }

graph = graph_builder.compile(
    checkpointer=checkpointer # Required for `interrupt` to work
)

# Run the graph until the interrupt
thread_config = {"configurable": {"thread_id": 1}}
graph.invoke("Hello!", config=thread_config)

