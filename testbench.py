import streamlit as st
from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_name):
    loader = PyPDFLoader(file_name)
    pages = []
    doc_data = ''
    for page in loader.lazy_load():
        pages.append(page)
        doc_data += page.page_content + '\n'
    return pages, doc_data

from langchain_community.document_loaders import PyPDFLoader
from portfolio_xml_tools import create_trade_from_term_sheet
from config_file import term_sheet_file


loader = PyPDFLoader(r'D:\Project_H\usd-inr-ccs-fixed-float.pdf')
pages = []
doc_data = ''
for page in loader.lazy_load():
    pages.append(page)
    doc_data += page.page_content + '\n'

term_sheet_file.term_sheet_data = doc_data

test = create_trade_from_term_sheet.invoke({})


class Foo:
    def __init__(self):
        self.term_sheet_data = "dummy string"

foo = Foo()
print(foo.term_sheet_data)
foo.term_sheet_data = "dummy string 1"
print(foo.term_sheet_data)

# st.title("PDF File Uploader")

# uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
# st.write("Uploaded file:")
# if uploaded_file is not None:
#     # st.write("File location: {}".format(uploaded_file.name))
#     st.write("File value: {}".format(load_pdf(uploaded_file.name)[1]))
