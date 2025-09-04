import os
import json
import dotenv
from datetime import datetime
from openai import OpenAI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

console = Console()

def render_conversation(conversation):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Role", style="cyan", no_wrap=True)
    table.add_column("Message", style="white")
    for message in conversation:
        role = message.get("role", "?")
        content = message.get("content", "")
        table.add_row(role, content)
    console.print(table)

def save_timeline(conversation, filename="timeline.txt", silent=False):
    """Save conversation to a timeline text file in the logs folder"""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    filepath = os.path.join(logs_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("Conversation Timeline\n")
        f.write("=" * 20 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, message in enumerate(conversation, 1):
            role = message.get("role", "unknown")
            content = message.get("content", "")
            f.write(f"{i}. {role.upper()}: {content}\n\n")
    
    if not silent:
        console.print(f"[bold green]Timeline saved to:[/bold green] {filepath}")

def save_conversation_json(conversation, filename="conversation.json", silent=False):
    """Save conversation to a JSON file in the logs folder"""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    filepath = os.path.join(logs_dir, filename)
    
    # Create a structured JSON object with metadata
    conversation_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_messages": len(conversation),
            "created_by": "statefulchat-old.py"
        },
        "conversation": conversation
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    if not silent:
        console.print(f"[bold blue]JSON conversation saved to:[/bold blue] {filepath}")

def save_both_formats(conversation, silent=False):
    """Save conversation in both text and JSON formats"""
    save_timeline(conversation, silent=silent)
    save_conversation_json(conversation, silent=silent)

def main():
    console.print(Panel.fit("Stateful Chatbot (Completions API) — Auto-saves timeline & JSON after each exchange", style="green"))
    model = "gpt-4o-mini"
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    # Auto-save initial state in both formats
    save_both_formats(conversation, silent=True)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            # Auto-save before exiting
            save_both_formats(conversation, silent=True)
            console.print("[bold green]Goodbye! Timeline & JSON saved automatically.[/bold green]")
            break
        # Show conversation context (all messages so far) without calling the API
        if user_input.strip().lower() == "context":
            console.print(Panel.fit("Context -> conversation between me and the model:", style="cyan"))
            render_conversation(conversation)
            continue
        # Manual save (optional - auto-save is already enabled)
        if user_input.strip().lower() == "save":
            save_both_formats(conversation)
            continue
        # Save only JSON format
        if user_input.strip().lower() == "json":
            save_conversation_json(conversation)
            continue
        # Save only text format
        if user_input.strip().lower() == "text":
            save_timeline(conversation)
            continue
        # Show available commands
        if user_input.strip().lower() == "help":
            console.print(Panel.fit("Commands: context, save, json, text, help, exit", style="yellow"))
            continue
            
        conversation.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model=model,
                messages=conversation
            )
            text = response.choices[0].message.content.strip()
            conversation.append({"role": "assistant", "content": text})
            render_conversation(conversation)
            
            # Auto-save after each complete exchange (user + assistant) in both formats
            save_both_formats(conversation, silent=True)
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
