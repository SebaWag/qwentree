#!/usr/bin/env python3
"""🌳 QwenTree — Multimodal Tree File Agent (CLI with Textual TUI).

Entry point: python -m qwentree
"""

import sys
import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, RichLog, Static, Tree
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.columns import Columns

from qwentree.core.config import settings
from qwentree.core.registry import auto_register_skills
from qwentree.tree import skill_tree
from qwentree.orchestrator import orchestrator


class QwenTreeApp(App):
    """🌳 QwenTree — Textual TUI Application."""

    TITLE = "🌳 QwenTree"
    SUB_TITLE = "Multimodal Tree File Agent — QwenCloud"
    CSS = """
    Screen {
        background: #1a1b26;
    }
    
    Header {
        background: #24283b;
        color: #a9b1d6;
    }
    
    Footer {
        background: #24283b;
        color: #565f89;
    }
    
    #main-container {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30%;
        min-width: 30;
        border-right: solid $primary;
        background: #1f2335;
        padding: 0 1;
    }
    
    #chat-area {
        width: 70%;
        height: 100%;
        padding: 0 1;
    }
    
    #chat-log {
        height: 85%;
        border: none;
        background: #1a1b26;
    }
    
    #input-container {
        height: 3;
        dock: bottom;
        padding: 0 1;
    }
    
    #command-input {
        background: #24283b;
        color: #c0caf5;
        border: solid #3b4261;
    }
    
    #command-input:focus {
        border: solid $accent;
    }
    
    #skill-tree {
        height: 70%;
        background: #1f2335;
        color: #c0caf5;
    }
    
    #status-bar {
        height: 3;
        background: #24283b;
        color: #565f89;
        padding: 0 1;
    }
    
    .info-label {
        color: #73daca;
    }
    
    .skill-icon {
        color: #bb9af7;
    }
    
    .user-msg {
        color: #7dcfff;
    }
    
    .assistant-msg {
        color: #c0caf5;
    }
    
    .error-msg {
        color: #f7768e;
    }
    
    .success-msg {
        color: #9ece6a;
    }
    
    Tree {
        background: #1f2335;
    }
    
    Tree:focus {
        border: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Salir"),
        Binding("ctrl+l", "clear", "Limpiar pantalla"),
        Binding("ctrl+r", "reset", "Resetear conversación"),
        Binding("ctrl+t", "toggle_sidebar", "Toggle sidebar"),
        Binding("tab", "focus_next", "Siguiente panel"),
    ]

    def __init__(self):
        super().__init__()
        self._app_ready = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="sidebar"):
                yield Static("📁 Skill Tree", classes="info-label")
                yield Tree("skills/", id="skill-tree")
                yield Static("", id="status-bar")
            with Vertical(id="chat-area"):
                yield RichLog(id="chat-log", highlight=True, markup=True)
                with Container(id="input-container"):
                    yield Input(
                        placeholder="> Escribe tu consulta para QwenTree...",
                        id="command-input",
                    )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Auto-register all skills
        self.log_info("🌳 Cargando QwenTree...")
        self._load_skills()
        self._populate_tree()
        self._show_welcome()
        self._app_ready = True

    def _load_skills(self):
        """Auto-discover and register all skills."""
        try:
            auto_register_skills()
            count = skill_tree.count()
            self.log_info(f"✅ {count} skills cargados desde el árbol")
        except Exception as e:
            self.log_error(f"Error cargando skills: {e}")

    def _populate_tree(self):
        """Populate the sidebar tree widget."""
        tree_widget = self.query_one("#skill-tree", Tree)
        tree_widget.clear()

        # Build tree from skill_tree
        root = tree_widget.root
        for cat_name, subdir in sorted(skill_tree.root.subdirs.items()):
            cat_node = root.add(f"📁 {cat_name}/", expand=True)
            for skill_name in sorted(subdir.skills.keys()):
                skill = subdir.skills[skill_name]
                cat_node.add_leaf(
                    f"📄 {skill_name}  — {skill.description[:40]}"
                )

    def _show_welcome(self):
        """Show welcome message."""
        chat = self.query_one("#chat-log", RichLog)
        welcome = Panel(
            f"[bold #bb9af7]🌳 QwenTree v0.1[/]\n\n"
            f"[#c0caf5]Multimodal Tree File Agent[/]\n"
            f"[#565f89]Powered by Qwen Cloud ({settings.active_model})[/]\n\n"
            f"[#73daca]Skills disponibles:[/] [bold]{skill_tree.count()}[/]\n"
            f"[#73daca]Categorías:[/] [bold]{len(skill_tree.root.subdirs)}[/]\n\n"
            f"[#565f89]Escribe tu consulta o escribe [bold]/help[/] para ayuda[/]",
            title="🚀 Bienvenido",
            border_style="#bb9af7",
        )
        chat.write(welcome)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input."""
        command = event.value.strip()
        if not command:
            return

        # Clear input
        input_widget = self.query_one("#command-input", Input)
        input_widget.value = ""

        # Show user message
        chat = self.query_one("#chat-log", RichLog)
        chat.write(Text(f"> {command}", style="bold #7dcfff"))

        # Handle special commands
        if command.startswith("/"):
            self._handle_slash_command(command)
            return

        # Process through orchestrator
        try:
            response = orchestrator.process(command)
            chat.write(Text(response, style="#c0caf5"))
        except Exception as e:
            chat.write(Text(f"❌ Error: {e}", style="bold #f7768e"))

        # Update status
        status = self.query_one("#status-bar", Static)
        history = orchestrator.get_history(1)
        status.update(
            f"[#565f89]🔄 {skill_tree.count()} skills | "
            f"🧠 {len(orchestrator.conversation_history)} mensajes | "
            f"🔮 {settings.active_model}[/]"
        )

    def _handle_slash_command(self, command: str):
        """Handle slash commands."""
        chat = self.query_one("#chat-log", RichLog)
        cmd = command.lower()

        if cmd == "/help":
            help_text = (
                "[bold #bb9af7]Comandos QwenTree[/]\n\n"
                "[bold #73daca]/help[/]      — Muestra esta ayuda\n"
                "[bold #73daca]/ls[/]        — Lista todos los skills\n"
                "[bold #73daca]/ls [cat][/]   — Skills de una categoría\n"
                "[bold #73daca]/tree[/]      — Muestra el árbol completo\n"
                "[bold #73daca]/stats[/]     — Estadísticas del agente\n"
                "[bold #73daca]/mode[/]      — Muestra modo actual (Qwen/Fallback)\n"
                "[bold #73daca]/reset[/]     — Resetea la conversación\n"
                "[bold #73daca]/clear[/]     — Limpia la pantalla\n\n"
                "[#565f89]O simplemente escribe tu consulta en lenguaje natural 🌟[/]"
            )
            chat.write(Markdown(help_text))

        elif cmd == "/ls":
            result = skill_tree.tree_display()
            chat.write(Text(f"\n{result}", style="#c0caf5"))

        elif cmd.startswith("/ls "):
            category = cmd[4:]
            skills = skill_tree.list_skills(category=category)
            if skills:
                text = "\n".join([str(s) for s in skills])
                chat.write(Text(text, style="#c0caf5"))
            else:
                chat.write(Text(f"❌ Categoría '{category}' no encontrada", style="#f7768e"))

        elif cmd == "/tree":
            display = skill_tree.tree_display()
            chat.write(Text(f"\n🌳 Skill Tree:\n{display}", style="#73daca"))

        elif cmd == "/stats":
            summary = skill_tree.summary()
            stats = (
                f"[bold #bb9af7]📊 QwenTree Stats[/]\n\n"
                f"[#73daca]Total skills:[/]  {summary['total_skills']}\n"
                f"[#73daca]Categorías:[/]    {summary['categories']}\n"
            )
            for cat, count in sorted(summary["skills_by_category"].items()):
                stats += f"  [#565f89]📁 {cat}/[/]  {count} skills\n"
            stats += (
                f"\n[#73daca]Modelo:[/]       {settings.active_model}\n"
                f"[#73daca]Modo API:[/]      {'☁️ Qwen Cloud' if settings.is_qwen_mode else '🔧 Fallback'}\n"
                f"[#73daca]Conversación:[/]  {len(orchestrator.conversation_history)} mensajes\n"
            )
            chat.write(Markdown(stats))

        elif cmd == "/mode":
            mode_text = (
                f"[bold #bb9af7]🔮 Modo Actual[/]\n\n"
                f"[#73daca]API Mode:[/]     {'☁️ Qwen Cloud' if settings.is_qwen_mode else '🔧 Fallback'}\n"
                f"[#73daca]Model:[/]       {settings.active_model}\n"
                f"[#73daca]Base URL:[/]    {settings.active_base_url}\n"
                f"[#73daca]Vision:[/]      {settings.qwen_vl_model}\n"
                f"[#73daca]Audio:[/]       {settings.qwen_audio_model}\n"
                f"[#73daca]Media Gen:[/]   {settings.qwen_image_model}\n"
            )
            chat.write(Markdown(mode_text))

        elif cmd == "/reset":
            orchestrator.reset()
            self.log_info("🔄 Conversación reseteada (memoria persistente intacta)")

        elif cmd == "/clear":
            chat.clear()
            self._show_welcome()

        else:
            chat.write(Text(f"Comando desconocido: {cmd}. Usa /help", style="#f7768e"))

    def log_info(self, message: str):
        """Log info message to chat."""
        chat = self.query_one("#chat-log", RichLog)
        chat.write(Text(f"ℹ️ {message}", style="#73daca"))

    def log_error(self, message: str):
        """Log error message to chat."""
        chat = self.query_one("#chat-log", RichLog)
        chat.write(Text(f"❌ {message}", style="bold #f7768e"))

    def action_toggle_sidebar(self):
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display

    def action_clear(self):
        """Clear chat."""
        chat = self.query_one("#chat-log", RichLog)
        chat.clear()
        self._show_welcome()

    def action_reset(self):
        """Reset conversation."""
        orchestrator.reset()
        self.log_info("🔄 Conversación reseteada")


def main():
    """Entry point for QwenTree CLI."""
    import sys

    # Check for --cli flag (non-TUI mode)
    if "--cli" in sys.argv:
        return _cli_mode()

    # Launch Textual TUI
    app = QwenTreeApp()
    app.run()


def _cli_mode():
    """Simple CLI mode (no Textual)."""
    print("🌳 QwenTree — Modo CLI")
    print(f"   Powered by Qwen Cloud ({settings.active_model})")
    print("   Escribe 'exit' para salir\n")

    auto_register_skills()
    print(f"   ✅ {skill_tree.count()} skills cargados\n")

    while True:
        try:
            user_input = input("🌳> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "salir"):
                break
            if user_input.startswith("/"):
                if user_input == "/ls":
                    print(skill_tree.tree_display())
                elif user_input == "/stats":
                    s = skill_tree.summary()
                    print(f"Skills: {s['total_skills']}, Categorías: {s['categories']}")
                elif user_input == "/mode":
                    print(f"Modo: {'Qwen' if settings.is_qwen_mode else 'Fallback'}")
                continue

            response = orchestrator.process(user_input)
            print(f"\n{response}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("👋 ¡Hasta luego!")


if __name__ == "__main__":
    main()
