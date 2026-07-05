"""🧠 QwenTree Orchestrator — The Brain.

Qwen-Max analyzes user queries and dynamically routes to the
appropriate skills from the skill tree. Uses tool calling to
decide which skills to invoke.

Flow:
1. User sends query
2. Orchestrator analyzes with Qwen-Max
3. Qwen decides which skill(s) to call (tool calling)
4. Skills execute and return results
5. Orchestrator consolidates response
"""

import json
from typing import Optional, Any
from datetime import datetime

from qwentree.core.qwen_client import qwen
from qwentree.core.config import settings
from qwentree.tree import skill_tree, SkillNode


# System prompt for the orchestrator
ORCHESTRATOR_SYSTEM_PROMPT = """You are QwenTree, a Tree File Agent — an AI that organizes its capabilities as a file tree.

## 🧠 Your Architecture
You have a tree of skills (capabilities) organized by category:
  skills/vision/     👁️  Image & video analysis
  skills/audio/      🎤  Speech recognition & synthesis  
  skills/video/      🎬  Video processing
  skills/code/       💻  Code execution & analysis
  skills/web/        🌐  Web scraping & search
  skills/files/      📁  File system operations
  skills/system/     ⚙️  System commands
  skills/memory/     🧠  Session memory & recall
  skills/media/      🎨  Image & video generation
  skills/integrations/ 🔗  External system integrations

## 🎯 Your Process
1. ANALYZE what the user wants
2. DECIDE which skill(s) to invoke from your tree
3. EXECUTE them in sequence or parallel
4. CONSOLIDATE results into a clear answer

## 🧠 Memory System
You have 3-tier hierarchical memory:
- 🏛️ MENTAL MODELS (highest): Canonical facts, never contradict
- 📝 OBSERVATIONS (medium): Learnings from past sessions
- 📦 RAW FACTS (lowest): Current conversation context

Always check memory first when the user refers to past interactions.

## 🌟 Multimodal Capabilities
You can see images, hear audio, watch videos, run code, browse the web,
and interact with the system — all through Qwen Cloud models."""


class Orchestrator:
    """Routes user queries to the appropriate skills using Qwen-Max."""

    def __init__(self):
        self.conversation_history: list[dict] = []
        self._init_system()

    def _init_system(self):
        """Initialize with system prompt + skill tree context."""
        tree_summary = skill_tree.summary()
        skills_list = "\n".join([
            f"  📁 {cat}/  ({count} skills)"
            for cat, count in sorted(tree_summary["skills_by_category"].items())
        ])

        system_content = (
            f"{ORCHESTRATOR_SYSTEM_PROMPT}\n\n"
            f"## 📋 Your Available Skills ({tree_summary['total_skills']} total)\n"
            f"{skills_list}\n\n"
            f"Current time: {datetime.now().isoformat()}"
        )

        self.conversation_history = [
            {"role": "system", "content": system_content}
        ]

    def _build_tools_from_skills(self) -> list[dict]:
        """Convert skill tree to OpenAI tool definitions."""
        tools = []
        for skill in skill_tree._all_skills.values():
            # Build a tool definition for each skill
            tool_def = {
                "type": "function",
                "function": {
                    "name": f"{skill.category}__{skill.name}",
                    "description": skill.description[:200],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": f"Input for {skill.name}",
                            }
                        },
                        "required": ["input"],
                    },
                },
            }
            tools.append(tool_def)

        # Add general tools
        tools.extend([
            {
                "type": "function",
                "function": {
                    "name": "search_memory",
                    "description": "Search across ALL memory tiers for past session data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_skills",
                    "description": "List available skills in a category",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Category to list (optional)"},
                        },
                    },
                },
            },
        ])
        return tools

    def process(self, user_message: str) -> str:
        """Process a user message through the orchestrator.

        Returns the consolidated response.
        """
        # Add user message
        self.conversation_history.append(
            {"role": "user", "content": user_message}
        )

        # Get available tools from skill tree
        tools = self._build_tools_from_skills()

        # Call Qwen-Max with tool calling
        response = qwen.chat_deep(
            self.conversation_history,
            tools=tools,
            temperature=0.3,
        )

        message = response.choices[0].message

        # Handle tool calls
        if message.tool_calls:
            return self._handle_tool_calls(message, user_message)

        # Pure text response
        reply = message.content
        self.conversation_history.append(
            {"role": "assistant", "content": reply}
        )
        return reply

    def _handle_tool_calls(self, message, original_message: str) -> str:
        """Execute tool calls and consolidate response."""
        self.conversation_history.append(message)

        tool_results = []
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}

            result = self._execute_tool(func_name, args)
            tool_results.append(result)

            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)[:3000],
            })

        # Get final consolidated response
        final = qwen.chat_deep(self.conversation_history)
        reply = final.choices[0].message.content

        self.conversation_history.append(
            {"role": "assistant", "content": reply}
        )
        return reply

    def _execute_tool(self, func_name: str, args: dict) -> Any:
        """Execute a tool call from the orchestrator."""
        # Special tools
        if func_name == "search_memory":
            return self._search_memory(args.get("query", ""))

        if func_name == "list_skills":
            category = args.get("category", "")
            skills = skill_tree.list_skills(category=category if category else None)
            return "\n".join([str(s) for s in skills])

        # Skill execution
        if "__" in func_name:
            category, skill_name = func_name.split("__", 1)
            skill = skill_tree.get_skill(f"{category}/{skill_name}")
            if skill:
                try:
                    input_data = args.get("input", "")
                    return skill.func(input_data)
                except Exception as e:
                    return f"Error executing {func_name}: {e}"

        return f"Unknown tool: {func_name}"

    def _search_memory(self, query: str) -> str:
        """Search across all memory tiers."""
        try:
            from qwentree.memory.retrieval_pipeline import RetrievalPipeline
            pipeline = RetrievalPipeline()
            result = pipeline.query(query)
            return result.get("formatted_context", "No results found")
        except Exception as e:
            return f"Memory search unavailable: {e}"

    def reset(self):
        """Reset conversation (memory persists)."""
        self._init_system()

    def get_history(self, last: int = 5) -> list[dict]:
        """Get last N exchanges."""
        exchanges = []
        for msg in self.conversation_history[-last*2:]:
            if msg["role"] in ("user", "assistant"):
                exchanges.append(msg)
        return exchanges[-last*2:]


# Singleton
orchestrator = Orchestrator()
