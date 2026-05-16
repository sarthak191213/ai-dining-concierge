from langchain_core.messages import HumanMessage, AIMessage


def format_chat_history(messages: list) -> list:
    """Keep only Human and AI messages, strip tool calls/results to prevent bloat."""
    formatted = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(msg)
        elif isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            formatted.append(AIMessage(content=msg.content))
    return formatted[-20:]  # keep last 20 messages max
