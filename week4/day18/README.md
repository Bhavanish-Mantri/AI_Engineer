# Day 18 - LangGraph Implementation - State, Nodes, Edges, and Conditional Edges

A practical introduction to implementing a basic workflow using **LangGraph**. This project focuses on understanding the core building blocks of LangGraph — **State, Nodes, Edges, Conditional Edges, Entry Points, and End Points** — without using any LLM or AI functionality.

The goal is to understand how LangGraph can convert a normal program flow into a structured graph-based workflow.

---

## 🎯 Overview

LangGraph can be understood as a framework for representing program logic as a **flow graph**. 

Instead of writing a large amount of `if-else` blocks, loops, and function-calling logic manually, we can represent the workflow using:

```text
State
  ↓
Nodes
  ↓
Edges
  ↓
Conditional Decisions
  ↓
Next Node
```

A LangGraph workflow mainly consists of three important concepts:
1. **State** - Shared data used by the workflow.
2. **Nodes** - Functions that perform work on the state.
3. **Edges** - Connections that determine what runs next.

Conditional edges allow the workflow to choose different paths based on the current state.

---

## 🤖 What is LangGraph?

LangGraph is a framework for building workflows as graphs. It is incredibly useful when a program contains multiple steps, decisions, loops, or different execution paths.

The basic idea can be understood using a flowchart:

```text
        START
          ↓
      Processing
          ↓
     ┌───────────┐
     │ Condition │
     └─────┬─────┘
       Yes │ No
           │
     ┌─────┴─────┐
     ↓           ↓
  Process      Process
     ↓           ↓
     └─────┬─────┘
           ↓
          END
```

LangGraph allows this exact type of flowchart to be represented directly in Python code.

---

## 🆚 Normal Python vs LangGraph

Consider a simple problem:
> Given a number, keep doubling it until it becomes greater than or equal to 100. Then print the final number.

**Normal Python Solution:**
```python
while n < 100:
    n = n * 2
print(n)
```

There is nothing wrong with this approach. However, as applications scale (especially AI Agents), managing complex loops and `while` loops becomes messy.

**LangGraph Approach:**
```text
State → Node → Decision → Node/Loop → END
```
LangGraph explicitly maps out the entire structure, making it highly scalable for complex decision-making processes.

---

## 🛠️ Core Components of LangGraph

A traditional flowchart translates into LangGraph concepts like this:

| Traditional Flowchart | LangGraph Concept |
|-----------------------|-------------------|
| Data / Variables      | **State**         |
| Processing Box        | **Node**          |
| Connection            | **Edge**          |
| Decision              | **Conditional Edge** |
| Start                 | **Entry Point**   |
| End                   | **END**           |

### 1. State (Shared Data)
The **State** is the shared data available to the nodes in the graph. Think of it as a **shared whiteboard** where different engineers (Nodes) can read from and write to. 

In Python, the state is represented using a `TypedDict`:
```python
class State(TypedDict):
    number: int
```

### 2. Nodes (Processing)
A **Node** represents a unit of work. In Python, a node is generally implemented as a function that reads the state and returns the updated state.
```python
def double(state: State):
    return {"number": state["number"] * 2}
```

### 3. Edges (Connections)
An **edge** connects nodes. It determines the execution path between nodes.
Example: `builder.add_edge("finish", END)`

### 4. Conditional Edges (Decisions)
A conditional edge chooses the next node based on a decision function.

---

## 🗣️ Decision Function & Conditional Edges

Not every function is a Node. A **Helper / Decision Function** is used to determine which edge should be followed.

```python
def decision(state: State):
    if state["number"] < 100:
        return "double"
    return "finish"
```

This decision creates a Conditional Edge:
```text
             Double
                │
                ↓
           Decision
           /       \
          /         \
      "double"    "finish"
        ↓             ↓
      Double        Finish
```

---

## 🔄 Complete Example Workflow

The complete workflow for the example is represented as:

```text
                  START
                    │
                    ↓
                 Double
                    │
                    ↓
                Decision
                /      \
               /        \
        number < 100   number >= 100
             │              │
             ↓              ↓
           Double         Finish
             │              │
             └───────┐      ↓
                     │     END
                     └───>
```

If we input `5`, the flow traces:
`5 → 10 → 20 → 40 → 80 → 160 → END`

---

## 🚀 Project Workflow

The implementation follows these major steps:

1. **Define State**: Create the TypedDict.
2. **Create Nodes**: Write standard Python functions to process state.
3. **Create Decision Functions**: Write functions returning the string name of the next route.
4. **Initialize StateGraph**: `builder = StateGraph(State)`
5. **Add Nodes**: `builder.add_node(...)`
6. **Set Entry Point**: `builder.set_entry_point(...)`
7. **Add Conditional Edges**: Define looping logic.
8. **Connect Final Node to END**: `builder.add_edge("finish", END)`
9. **Compile Graph**: `graph = builder.compile()`
10. **Invoke Graph**: Run with `graph.invoke(...)`

---

## 💡 Key Learnings

By completing this project, you will understand:
- What LangGraph is and how it replaces standard flow control loops.
- What **State** is and why it acts like a "shared whiteboard".
- How Python functions are transformed into **Nodes**.
- The difference between standard **Edges** and **Conditional Edges**.
- How a **decision function** determines execution routing.
- The lifecycle of building, compiling, and invoking a StateGraph.
- That LangGraph is an orchestration framework and does **not** inherently require an LLM to be useful.

---

## ✨ Summary: The Important Concept

**STATE** → Shared Whiteboard  
**NODE** → Person working on the whiteboard  
**EDGE** → Connection between people  
**CONDITIONAL EDGE** → Decision about who works next  
**ENTRY POINT** → First person to work  
**END** → Workflow finished  

Once these fundamentals are clear, using LangGraph to build complex AI Agents involving tools, LLMs, RAG, and multi-step reasoning becomes significantly easier.
