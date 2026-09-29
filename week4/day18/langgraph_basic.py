from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

# ============================================================
# 1. STATE
# ============================================================
# State is the shared data/whiteboard of the graph.
# Our graph only needs one piece of data: number.

class State(TypedDict):
    number: int


# ============================================================
# 2. NODE: DOUBLE
# ============================================================
# This node:
# 1. Reads the current number from State
# 2. Doubles it
# 3. Returns the updated number
#
# A LangGraph node receives State and returns a dictionary
# containing the State updates.

def double(state: State) -> dict:
    current_number = state["number"]

    new_number = current_number * 2

    print(f"Doubling: {current_number} -> {new_number}")

    return {
        "number": new_number
    }


# ============================================================
# 3. NODE: FINISH
# ============================================================
# This node reads the final number and prints it.
# It does not actually change the State.

def finish(state: State) -> dict:
    number = state["number"]

    print(f"Finished! Final number: {number}")

    return {
        "number": number
    }


# ============================================================
# 4. DECISION / HELPER FUNCTION
# ============================================================
# IMPORTANT:
#
# This is NOT a graph node.
#
# Its job is only to decide where the graph should go next.
#
# If number < 100:
#       go back to "double"
#
# Otherwise:
#       go to "finish"

def decision(state: State) -> str:

    if state["number"] < 100:
        return "double"

    return "finish"


# ============================================================
# 5. CREATE GRAPH
# ============================================================

builder = StateGraph(State)


# ============================================================
# 6. ADD NODES
# ============================================================

builder.add_node("double", double)
builder.add_node("finish", finish)


# ============================================================
# 7. SET ENTRY POINT
# ============================================================
# The graph starts execution from the "double" node.

builder.set_entry_point("double")


# ============================================================
# 8. ADD CONDITIONAL EDGE
# ============================================================
#
# Starting node:
#       double
#
# Decision function:
#       decision
#
# Possible results:
#
#       "double" -> double node
#       "finish" -> finish node
#

builder.add_conditional_edges(
    "double",
    decision,
    {
        "double": "double",
        "finish": "finish"
    }
)


# ============================================================
# 9. CONNECT FINISH TO END
# ============================================================

builder.add_edge("finish", END)


# ============================================================
# 10. COMPILE GRAPH
# ============================================================

graph = builder.compile()


# ============================================================
# 11. RUN GRAPH
# ============================================================

if __name__ == "__main__":

    initial_state = {
        "number": 23
    }

    result = graph.invoke(initial_state)

    print("\nFinal State:")
    print(result)