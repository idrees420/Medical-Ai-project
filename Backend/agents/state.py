from typing import TypedDict, Annotated, List, Optional, Union
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next_agent: Optional[str]
    doctor_found: Optional[dict]
    booking_details: Optional[dict]
    user_request: Optional[str]
    user_email: Optional[str]
