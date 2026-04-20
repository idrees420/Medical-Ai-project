from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents import supervisor_node, info_node, booking_node, end_node

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("InfoAgent", info_node)
workflow.add_node("BookingAgent", booking_node)
workflow.add_node("EndAgent", end_node)

# Define the conditional edge logic
def get_next_node(state: AgentState):
    next_agent = state.get("next_agent")
    if next_agent == "USER":
        return END
    return next_agent

# Add edges
workflow.set_entry_point("Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    get_next_node,
    {
        "InfoAgent": "InfoAgent",
        "BookingAgent": "BookingAgent",
        "EndAgent": "EndAgent",
        END: END
    }
)

workflow.add_edge("InfoAgent", END)
workflow.add_edge("BookingAgent", END)
workflow.add_edge("EndAgent", END)

# Compile the graph
app = workflow.compile()

from langchain_core.messages import HumanMessage

def run_agents(user_input, chat_history=None, user_email=None):
    if chat_history is None:
        chat_history = []

    # Send only the new message to the graph
    # The graph state already contains previous messages if we pass them in inputs
    inputs = {
        "messages": chat_history + [HumanMessage(content=user_input)],
        "user_email": user_email
    }

    final_response = "I'm sorry, I couldn't process that request."
    updated_history = chat_history.copy()
    updated_history.append(HumanMessage(content=user_input))

    print(f"--- Executing Graph for input: {user_input} ---")
    
    try:
        for output in app.stream(inputs, config={"recursion_limit": 20}):
            for key, value in output.items():
                print(f"Node '{key}' finished.")
                if "messages" in value:
                    new_msgs = value["messages"]
                    for m in new_msgs:
                        updated_history.append(m)
                        if hasattr(m, "content") and m.content:
                            final_response = m.content
    except Exception as e:
        print(f"ERROR in run_agents: {e}")
        if "503" in str(e) or "unreachable_backend" in str(e):
            final_response = "I'm currently having trouble connecting to the AI service (Mistral is experiencing issues). Please try again in a few moments."
        else:
            final_response = "I encountered an error while processing your request. Please try again."

    return {
        "response": final_response,
        "chat_history": updated_history
    }
