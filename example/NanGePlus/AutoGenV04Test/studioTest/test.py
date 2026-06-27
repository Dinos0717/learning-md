import os
import asyncio
from autogenstudio.teammanager import TeamManager
from autogen_agentchat.base import TaskResult
from autogen_agentchat.ui import Console


async def main() -> None:
    tm = TeamManager()
    stream = tm.run_stream(task="你好", team_config="team-config.json")
    await Console(stream)

if __name__ == '__main__':
    asyncio.run(main())