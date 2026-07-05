"""Confucius Agent — Main Agent with Hierarchical Memory.

Integrates the 3-tier memory system with Qwen Cloud LLM.
Supports tool calling, multi-turn conversations, and cross-session memory.
"""

from typing import Optional

from qwentree.core.qwen_client import qwen
import json
from qwentree.memory.retrieval_pipeline import RetrievalPipeline


# Tool definitions for the agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_mental_model",
            "description": "Store canonical knowledge (highest priority memory). Use for company policies, rules, verified facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The knowledge to store"},
                    "source": {"type": "string", "description": "Source of this knowledge"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["content", "source"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_observation",
            "description": "Store a learning or pattern from this session (medium priority).",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The observation"},
                    "category": {"type": "string", "description": "Category (general, code, decision, pattern)"},
                    "confidence": {"type": "number", "description": "Confidence 0.0-1.0"},
                },
                "required": ["content"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search across ALL memory tiers (Mental Models + Observations + Raw Facts). Use for any question about past interactions or stored knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Filter by category"},
                },
                "required": ["query"],
            },
        }
    },
]


class ConfuciusAgent:
    """Agent with 3-tier hierarchical memory, powered by Qwen Cloud."""

    def __init__(self, system_prompt: Optional[str] = None):
        self.memory = RetrievalPipeline()
        self.conversation_history: list[dict] = []
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt,
        })

    def _default_system_prompt(self) -> str:
        return """You are Confucius Agent, an AI assistant with hierarchical memory.

Your memory has THREE tiers, each with different priority:

1. 🏛️ MENTAL MODELS (highest priority)
   Canonical knowledge — company policies, rules, verified facts.
   These are your source of truth. Never contradict them.

2. 📝 OBSERVATIONS (medium priority)
   Persistent learnings from past sessions — patterns, decisions, notes.
   Use them for context but verify against Mental Models.

3. 📦 RAW FACTS (lowest priority, auto-expires)
   Ephemeral context — current conversation, temporary data.
   Useful for immediate context but not reliable long-term.

When answering:
- ALWAYS check Mental Models first (canonical knowledge overrides everything)
- Use Observations for context and patterns
- Use Raw Facts for immediate conversation history
- If information contradicts between tiers, trust Mental Models
"""

    def process_message(self, user_message: str) -> str:
        """Process a user message with full memory retrieval."""
        # 1. Retrieve relevant context from all memory tiers
        memory_context = self.memory.query(user_message)
        context_str = memory_context["formatted_context"]

        # 2. Add context to conversation
        context_msg = {
            "role": "system",
            "content": f"[MEMORY RETRIEVAL]\n{context_str}",
        }
        messages = [context_msg] + self.conversation_history[-10:] + [
            {"role": "user", "content": user_message},
        ]

        # 3. Get response from LLM (Qwen Cloud or fallback)
        response = qwen.chat(messages, tools=TOOLS)

        # 4. Handle tool calls
        if response.choices[0].message.tool_calls:
            return self._handle_tool_calls(response, user_message)

        # 5. Store interaction as raw fact
        assistant_reply = response.choices[0].message.content
        self.memory.add_raw_fact(
            content=f"Q: {user_message}\nA: {assistant_reply}",
            channel="session",
        )
        self.conversation_history.append(
            {"role": "user", "content": user_message}
        )
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_reply}
        )

        return assistant_reply

    def _handle_tool_calls(self, response, original_message: str) -> str:
        """Execute tool calls and continue the conversation."""
        assistant_msg = response.choices[0].message
        self.conversation_history.append(
            {"role": "user", "content": original_message}
        )
        self.conversation_history.append(assistant_msg)

        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            args = tool_call.function.arguments

            args_dict = json.loads(args)

            if func_name == "add_mental_model":
                result = self.memory.add_mental_model(
                    args_dict["content"],
                    args_dict.get("source", "agent"),
                    args_dict.get("tags"),
                )
                observation = f"✅ Stored as Mental Model (id: {result})"

            elif func_name == "add_observation":
                self.memory.add_observation(
                    args_dict["content"],
                    args_dict.get("category", "general"),
                    args_dict.get("confidence", 1.0),
                )
                observation = "✅ Observation stored"

            elif func_name == "search_memory":
                results = self.memory.query(
                    args_dict["query"],
                    category=args_dict.get("category"),
                )
                observation = results["formatted_context"]

            else:
                observation = f"Unknown tool: {func_name}"

            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": observation,
            })

        # Get final response after tool execution
        final = qwen.chat(self.conversation_history[-15:])
        reply = final.choices[0].message.content

        self.conversation_history.append(
            {"role": "assistant", "content": reply}
        )
        return reply

    def reset_conversation(self):
        """Start fresh conversation (but memory persists)."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
