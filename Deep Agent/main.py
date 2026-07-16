import sys
from langchain_core.messages import BaseMessage
from agents import build_agent
from config import PROJECTS_DIR
from logger import logger

# Terminal decorative banner
BANNER = r"""
   _____ _                 __        ______          ___
  / ___/(_)___ ___  ____  / /__     / ____/___  ____/ (_)___  ____ _
  \__ \/ / __ `__ \/ __ \/ / _ \   / /   / __ \/ __  / / __ \/ __ `/
 ___/ / / / / / / / /_/ / /  __/  / /___/ /_/ / /_/ / / / / / /_/ /
/____/_/_/ /_/ /_/ .___/_/\___/   \____/\____/\__,_/_/_/ /_/\__, /
                /_/                                        /____/
"""

def execute_agent_loop(agent) -> None:
    """Handles runtime console interaction with the Deep Agent."""
    print(BANNER)
    print("Plan -> Write -> Sandbox Run -> Review -> Fix -> Deliver")
    print("=" * 60)
    print(f"Projects base workspace target: {PROJECTS_DIR}\n")
    print("Describe a coding task. Type 'quit' or 'exit' to finish.\n")

    task_count = 0

    while True:
        try:
            # Capture user input cleanly
            user_input = input("> ").strip()
            
            if user_input.lower() in ("quit", "exit", "q"):
                print("Exiting application safely. Goodbye!")
                break
                
            if not user_input:
                continue

            task_count += 1
            
            # Thread configuration keeps conversational history isolated per task session
            config = {"configurable": {"thread_id": f"task-{task_count}"}}

            print("\n" + "-" * 30 + " Agent Stream Init " + "-" * 30)
            
            # Stream graph state modifications updates step-by-step
            for step in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
                stream_mode="updates"
            ):
                for _, update in step.items():
                    if update and (messages := update.get("messages")):
                        # Handle both single message objects and lists of messages safely
                        messages_list = messages if isinstance(messages, list) else [messages]
                        for message in messages_list:
                            if isinstance(message, BaseMessage):
                                # Pretty prints structured token responses & tool call indicators
                                message.pretty_print()
                                
            print("-" * 30 + " Agent Stream End " + "-" * 30 + "\n")

        except KeyboardInterrupt:
            print("\nSession interrupted via keyboard. Exiting safely.")
            break
        except Exception as e:
            # Catch exceptions at the loop level so a single runtime crash doesn't kill the CLI session
            logger.error(f"An unexpected error occurred processing your request: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        logger.info("Initializing multi-agent graph dependencies...")
        # Programmatically construct the multi-agent graph via the factory function
        agent_instance = build_agent()
        
        # Start the interactive workspace loop
        execute_agent_loop(agent_instance)
        
    except Exception as initialization_error:
        logger.critical(f"Failed to bootstrap the coding agent runtime: {initialization_error}")
        sys.exit(1)