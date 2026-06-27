from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message
import asyncio
from metagpt.context import Context
from metagpt.logs import logger
import re
import subprocess



# 定义Action1
# 定义一个继承自 Action 的类 SimpleWriteCode，表示该动作的职责是编写Python脚本
class SimpleWriteCode(Action):
    PROMPT_TEMPLATE: str = """
    Write a python function that can {instruction} and provide two runnnable test cases.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """

    name: str = "SimpleWriteCode"

    async def run(self, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)
        rsp = await self._aask(prompt)
        code_text = SimpleWriteCode.parse_code(rsp)
        return code_text

    @staticmethod
    def parse_code(rsp):
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text

# 定义Action2
# 定义一个继承自 Action 的类 SimpleRunCode，表示该动作的职责是运行Python脚本
class SimpleRunCode(Action):
    name: str = "SimpleRunCode"

    async def run(self, code_text: str):
        result = subprocess.run(["python3", "-c", code_text], capture_output=True, text=True)
        code_result = result.stdout
        logger.info(f"{code_result=}")
        return code_result


# 定义Role
class SimpleCoder(Role):
    name: str = "NanGe"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteCode, SimpleRunCode])
        # 动作执行模式  按顺序执行
        self._set_react_mode(react_mode="by_order")

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        code_text = await todo.run(msg.content)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        # 保存记忆
        self.rc.memory.add(msg)
        return msg


# 运行Role测试
async def main():
    msg = "编写一个python脚本实现列表求和"
    context = Context()
    role = SimpleCoder(context=context)
    logger.info(msg)
    result = await role.run(msg)
    logger.info(result)



if __name__ == '__main__':
    asyncio.run(main())