"""Interactive CLI for the company AI assistant."""

import asyncio
import sys
from uuid import uuid4
from config.settings import settings
from graph import run_agent_graph


def print_welcome():
    """Display welcome message with agent capabilities."""
    print("\n" + "=" * 70)
    print("  COMPANY AI ASSISTANT")
    print("=" * 70)
    print("\nI can help with:")
    print("  • Company holidays and working days")
    print("  • HR policies and leave information")
    print("  • Upcoming company events")
    print("  • Employee and team information")
    print("  • General company questions")
    print("\nType 'exit' to quit or 'help' for commands.")
    print("=" * 70 + "\n")


def print_help():
    """Display available commands."""
    print("\nCommands:")
    print("  exit    - Quit")
    print("  help    - Show this help")
    print("  clear   - Clear history")
    print("  history - Show conversation\n")


async def main():
    """Run the interactive chat loop."""
    try:
        settings.validate()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print_welcome()
    thread_id = str(uuid4())
    history = []

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == "exit":
                print("\nGoodbye!")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if user_input.lower() == "clear":
                thread_id = str(uuid4())
                history = []
                print("[OK] History cleared.\n")
                continue

            if user_input.lower() == "history":
                if history:
                    print("\n--- Conversation History ---")
                    for i, (u, a, r) in enumerate(history, 1):
                        print(f"\n[{i}] You: {u}")
                        print(f"    {a}: {r[:150]}...")
                    print("\n--- End ---\n")
                else:
                    print("\nNo history yet.\n")
                continue

            # Get response from agent graph
            print("Assistant: [Processing...]", end="", flush=True)
            response, agent_key = await run_agent_graph(user_input, thread_id)
            print("\r" + " " * 50 + "\r", end="")
            
            # Get display name for the agent
            from agents.supervisor import AGENT_DISPLAY_NAMES
            agent_display_name = AGENT_DISPLAY_NAMES.get(agent_key, "Unknown Agent")
            
            print(f"Assistant: {response}")
            print(f"  [{agent_display_name}]\n")

            history.append((user_input, agent_display_name, response))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
