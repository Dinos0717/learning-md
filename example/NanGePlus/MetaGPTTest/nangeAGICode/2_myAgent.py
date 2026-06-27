from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message
import asyncio
from metagpt.context import Context
from metagpt.logs import logger
import re



# 定义Action
# 定义一个继承自 Action 的类 SimpleWriteCode，表示该动作的职责是编写Python脚本
class SimpleWriteCode(Action):
    # 定义Prompt模版
    PROMPT_TEMPLATE: str = """
    Write a python function that can {instruction} and provide two runnnable test cases.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """

    name: str = "SimpleWriteCode"

    async def run(self, instruction: str):
        # 使用模版动态生成输入prompt
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)
        # 调用LLM，获取生成结果
        rsp = await self._aask(prompt)
        # 返回提取出的 Python 代码
        code_text = SimpleWriteCode.parse_code(rsp)
        return code_text

    # 解析代码
    # 使用正则表达式从 LLM 返回结果中提取 Python 代码块
    # 支持多行解析（re.DOTALL），匹配以 ```python 开头并以 ``` 结尾的代码
    @staticmethod
    def parse_code(rsp):
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text


# 定义Role
# 定义一个继承自 Role 的类 SimpleCoder，表示智能体的行为由该角色驱动
class SimpleCoder(Role):
    name: str = "NanGe"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 绑定该角色可以执行的动作
        self.set_actions([SimpleWriteCode])

    # 自定义动作逻辑
    # 适用于Action需要多个输入的情况、希望修改输入、使用特定记忆、或进行任何其他更改以反映特定逻辑的情况
    async def _act(self) -> Message:
        # 日志记录当前的角色设置和待办事项
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        # 将当前的任务对象赋值给变量，表示接下来将执行的动作
        todo = self.rc.todo
        # 获取消息上下文 从角色的记忆中获取相关的上下文信息  特定数量的消息，可以指定参数 k=1 表示最新消息
        msg = self.get_memories(k=1)[0]
        # 执行当前任务 传递获取到的上下文信息作为输入
        code_text = await todo.run(msg.content)
        # 创建一个新的 Message 对象
        # content: 动作的输出内容，即生成的代码文本
        # role: 当前角色的名称
        # cause_by: 导致该消息的任务类型
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        # 将生成的消息返回，以便团队中的其他角色或系统处理
        return msg


# 运行Role测试
async def main():
    # 定义初始消息
    msg = "编写一个python脚本实现列表求和"
    # 提供环境 即创建上下文
    context = Context()
    # 实例化角色
    role = SimpleCoder(context=context)
    logger.info(msg)
    # 运行角色
    result = await role.run(msg)
    logger.info(result)



if __name__ == '__main__':
    asyncio.run(main())