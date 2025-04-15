from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override = True)

# llm = ChatAnthropic(
#     model="claude-3-5-haiku-latest",
#     temperature=0,
#     timeout=None,
#     max_retries=2,
#     # other params...
# )
llm = ChatAnthropic(
    model="claude-3-5-sonnet-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)

llm_37 = ChatAnthropic(
    model="claude-3-7-sonnet-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)
