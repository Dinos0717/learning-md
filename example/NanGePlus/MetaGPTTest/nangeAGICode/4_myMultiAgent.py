import re
import asyncio
from metagpt.config2 import Config
from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team




# 解析代码
def parse_code(rsp):
    pattern = r"```python(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text


# 定义Action
# 定义一个继承自 Action 的类 SimpleWriteCode，表示该动作的职责是编写Python脚本
class SimpleWriteCode(Action):

    PROMPT_TEMPLATE: str = """
    Write a python function that can {instruction}.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """
    name: str = "SimpleWriteCode"

    async def run(self, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        return code_text


# 定义Action
# 定义一个继承自 Action 的类 SimpleWriteTest，表示该动作的职责是提供测试用例，生成单元测试代码
class SimpleWriteTest(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    Write {k} unit tests using pytest for the given function, assuming you have imported it.
    Return ```python your_code_here ``` with NO other texts,
    your code:
    """

    name: str = "SimpleWriteTest"
    # 使用上下文信息 context 和数量参数 k
    async def run(self, context: str, k: int = 3):
        prompt = self.PROMPT_TEMPLATE.format(context=context, k=k)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        return code_text


# 定义Action3
# 定义一个继承自 Action 的类 SimpleWriteReview，审查来自 SimpleWriteTest 输出的测试用例，并检查其覆盖范围和质量
class SimpleWriteReview(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    Review the test cases and provide one critical comments:
    """

    name: str = "SimpleWriteReview"

    async def run(self, context: str):
        prompt = self.PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)
        return rsp


# 定义Role 编写代码
class SimpleCoder(Role):
    name: str = "Alice"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([SimpleWriteCode])


# 定义Role 基于编写的代码提供测试用例
class SimpleTester(Role):
    name: str = "Bob"
    profile: str = "SimpleTester"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 负责生成代码创建测试用例
        self.set_actions([SimpleWriteTest])
        # 可同时监视代码生成和测试评审的消息
        self._watch([SimpleWriteCode])
        # self._watch([SimpleWriteCode, SimpleWriteReview])

    # 自定义动作逻辑
    # 适用于Action需要多个输入的情况、希望修改输入、使用特定记忆、或进行任何其他更改以反映特定逻辑的情况
    async def _act(self) -> Message:
        # 日志记录当前的角色设置和待办事项
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        # 将当前的任务对象赋值给变量，表示接下来将执行的动作
        todo = self.rc.todo
        # 获取消息上下文 从角色的记忆中获取相关的上下文信息  特定数量的消息，可以指定参数 k=1 表示最新消息
        # context = self.get_memories(k=1)[0].content
        # 调用全部消息
        context = self.get_memories()
        # 执行当前任务 传递获取到的上下文信息作为输入 k=5: 指定生成 5 个单元测试
        code_text = await todo.run(context, k=5)
        # 创建一个新的 Message 对象
        # content: 动作的输出内容，即生成的代码文本
        # role: 当前角色的名称
        # cause_by: 导致该消息的任务类型
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        # 将生成的消息返回，以便团队中的其他角色或系统处理
        return msg


# 定义Role 审查测试用例，检查其覆盖范围和质量
class SimpleReviewer(Role):
    name: str = "Charlie"
    profile: str = "SimpleReviewer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([SimpleWriteReview])
        self._watch([SimpleWriteTest])


# 运行Team测试
# idea:用户初始消息
# investment:能用于模拟开发资源或评估开发成本
# n_round:需要运行的迭代次数
# add_human:指定是否在团队中添加一个人类角色
async def main(idea, investment, n_round, add_human):
    logger.info(idea)
    # 实例化一个team
    team = Team()
    # 将角色添加到团队中
    team.hire(
        [
            SimpleCoder(),
            SimpleTester(),
            SimpleReviewer(is_human=add_human),
        ]
    )
    # 调用 team.invest() 方法，将初始资金分配给团队 潜在作用:资金可能影响团队的执行效率或完成质量（例如更快生成结果，或更细致的审查）
    team.invest(investment=investment)
    # 启动项目 用于定义项目的核心功能需求，驱动团队内部各角色的任务执行
    team.run_project(idea)
    # 在多个迭代轮次中执行团队任务
    await team.run(n_round=n_round)


if __name__ == "__main__":
    idea = "编写一个python脚本实现列表乘积"
    investment = 3.0
    n_round = 5
    add_human = False
    # add_human = True

    asyncio.run(main(idea, investment, n_round, add_human))