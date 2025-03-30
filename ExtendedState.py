from langgraph.graph import MessagesState
from typing import Annotated, List, Tuple, Literal, Optional, Dict

class State(MessagesState):
    next_agent:  Annotated[Optional[str], "Next agent to be called based on current task and tools description of the agent."]
    next_task:  Annotated[Optional[str], "Task to be performed by next agent based on current task and tools description of the agent."]
    stopping_criteria:  Annotated[Optional[str], "Stopping criteria for current agent to be defined based on current task and tools description of the agent."]
    summary:  Annotated[Optional[str], "Summary of the tasks performed so far and also past summary. This is to keep track of past actions and thier outcomes and also to provide context to next task. Should be blank if there is no task performed so far, Should be clear and consise eg: 1. <task performed>:<task outcome>, 2. <task performed>:<task outcome>"]
    is_completed:  Annotated[Optional[Literal["True", "False"]], "Is the task completed or not. Should be True if the task is completed, False otherwise."]