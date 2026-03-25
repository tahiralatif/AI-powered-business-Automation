from agents import AgentHooks, RunContextWrapper, TContext, AgentBase, Tool 

from typing_extensions import TypeVar
TAgent = TypeVar("TAgent", bound=AgentBase, default=AgentBase)



class AgentBasedHooks(AgentHooks):

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
    ) -> None:
        """Called concurrently with tool invocation."""
        print(f"Tool {tool.name} is starting...")
        print(f"Tool Agent: {agent.name}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print(f"Tool {tool.name} has finished.")
        print(f"Result: {result}")
