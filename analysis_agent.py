from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_anthropic import ChatAnthropic
import pandas as pd

llm = ChatAnthropic(
    model="claude-3-5-haiku-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)
 
df = pd.read_csv(r"D:\Project_H\Examples\Example_5\ExpectedOutput\exposure_nettingset_CPTY_A.csv")
agent = create_pandas_dataframe_agent(
    llm, df, agent_type="zero-shot-react-description", verbose=True, allow_dangerous_code=True, max_iterations=2, include_df_in_prompt=True, number_of_head_rows=3,
    agent_executor_kwargs= {"handle_parsing_errors":True}, return_intermediate_steps=True
)
