from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from agent.prompts import SYSTEM_PROMPT
from agent.tools import ALL_TOOLS


def create_agent(model_name: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model_name, temperature=0.3)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: MessagesState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()


def run_agent(user_input: str, chat_history: list = None, model_name: str = "gpt-4o-mini"):
    agent = create_agent(model_name)

    messages = []
    if chat_history:
        messages.extend(chat_history)
    messages.append(HumanMessage(content=user_input))

    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content, result["messages"]
