"""
基于 FastAPI Agent API 的 Gradio Web 界面（12_AgentAPIServerWithSkills，含 Skill 能力）
后端地址与端口从本目录 utils.config 读取
"""

import gradio as gr
import requests
import json
import time
import re
from typing import List, Dict, Any
# 使用本目录配置
from utils.config import Config

# =============================================
# 配置区（从 Config 读取）
# =============================================
BASE_URL = Config.API_BASE_URL
USER_ID = "user_001"
THREAD_ID = "gradio_thread_" + str(int(time.time()))

# 全局变量：保存当前中断信息（待审核的工具调用等）
current_interrupt_info: Dict[str, Any] = None


def send_message(message: str, history: List[Dict[str, str]]):
    """
    统一处理用户输入：
    - 普通问题 → 调用 /ask（含 Skill 能力：摘要、翻译等）
    - 审核指令（同意/拒绝/编辑等） → 调用 /intervene
    """
    global current_interrupt_info

    if not message.strip():
        history.append({"role": "assistant", "content": "请输入内容"})
        return history

    # 先把用户消息加到历史
    history.append({"role": "user", "content": message})

    lower_msg = message.lower().strip()

    # 关键词定义
    approve_keywords = ["同意", "通过", "yes", "ok", "允许", "确认", "y", "approve"]
    reject_keywords = ["拒绝", "no", "不允许", "禁止", "否", "n", "reject"]
    exit_keywords = ["退出", "stop", "结束", "cancel", "q"]
    help_keywords = ["帮助", "help"]
    edit_keywords = ["编辑", "edit", "修改", "改", "change"]

    is_approve = any(kw in lower_msg for kw in approve_keywords)
    is_reject = any(kw in lower_msg for kw in reject_keywords)
    is_exit = any(kw in lower_msg for kw in exit_keywords)
    is_help = any(kw in lower_msg for kw in help_keywords)
    is_edit = any(kw in lower_msg for kw in edit_keywords)

    # 若当前处于中断状态，则按审核指令处理
    if current_interrupt_info:
        actions = current_interrupt_info.get("action_requests", [])
        if not actions:
            history.append({"role": "assistant", "content": "当前没有待审核的工具调用"})
            current_interrupt_info = None
            return history

        # 处理退出
        if is_exit:
            history.append({"role": "assistant", "content": "已退出本次对话。需要重新开始请清空会话或输入新问题。"})
            current_interrupt_info = None
            return history

        # 处理帮助
        if is_help:
            help_text = """
**审核帮助：**
- `同意` / `通过` / `yes` / `ok` → 全部允许执行
- `拒绝` / `no` → 全部禁止执行
- `编辑 N {新参数JSON}` → 编辑第 N 个工具的参数（N 从 0 开始）
  示例：编辑 1 {"city": "上海"}
  或：编辑第2个 {"new_key": "value"}
- `退出` / `stop` → 结束对话
- `帮助` → 显示此帮助

支持混合：`同意，但编辑 0 {"city": "广州"}`
直接回复关键词或指令即可。
"""
            history.append({"role": "assistant", "content": help_text})
            return history

        # 处理编辑指令（优先匹配编辑，再决定其他默认 approve）
        decisions = []
        edit_found = False

        # 尝试匹配编辑指令（支持多种写法）
        edit_pattern = r"(?:编辑|edit|修改|改|change)\s*(?:第)?\s*(\d+)\s*(?:个|工具)?\s*(?:参数)?\s*({.*})"
        matches = re.findall(edit_pattern, message, re.IGNORECASE | re.DOTALL)

        if matches or is_edit:
            edit_found = True
            edited_indices = set()

            for idx_str, new_args_str in matches:
                try:
                    idx = int(idx_str.strip())
                    if 0 <= idx < len(actions):
                        new_args = json.loads(new_args_str.strip())
                        edited_action = {"name": actions[idx]["name"], "args": new_args}
                        decisions.append({"type": "edit", "edited_action": edited_action})
                        edited_indices.add(idx)
                        history.append({"role": "assistant", "content": f"已记录编辑：第 {idx} 个工具参数改为 {json.dumps(new_args, ensure_ascii=False)}"})
                    else:
                        history.append({"role": "assistant", "content": f"索引 {idx} 超出范围（共 {len(actions)} 个工具）"})
                except (ValueError, json.JSONDecodeError) as e:
                    history.append({"role": "assistant", "content": f"编辑参数解析失败：{str(e)}\n请使用合法 JSON 格式"})

            for i in range(len(actions)):
                if i not in edited_indices:
                    decisions.append({"type": "approve"})

        if not edit_found:
            if is_approve:
                decisions = [{"type": "approve"} for _ in actions]
                action_msg = "**您选择了：全部同意** 正在继续执行..."
            elif is_reject:
                decisions = [{"type": "reject"} for _ in actions]
                action_msg = "**您选择了：全部拒绝** 正在处理..."
            else:
                history.append({"role": "assistant", "content": "未识别到有效指令。请回复「同意」「拒绝」「编辑 N {参数}」「帮助」等"})
                return history

            history.append({"role": "assistant", "content": action_msg})

        payload = {"thread_id": THREAD_ID, "user_id": USER_ID, "decisions": decisions}

        try:
            resp = requests.post(f"{BASE_URL}/intervene", json=payload, timeout=60)
            if resp.status_code != 200:
                history.append({"role": "assistant", "content": f"审核提交失败：{resp.status_code} {resp.text}"})
                current_interrupt_info = None
                return history

            data = resp.json()

            if data.get("status") == "completed":
                result = data.get("result", "").strip()
                history.append({"role": "assistant", "content": f"**执行完成！**\n\n最终回答：\n{result}"})
                current_interrupt_info = None
                return history

            elif data.get("status") == "interrupted":
                current_interrupt_info = data.get("interrupt_details", {})
                actions = current_interrupt_info.get("action_requests", [])
                interrupt_text = "\n**⚠️ 仍有新的待审核项**\n\nAgent 继续执行后，又遇到需要您确认的工具调用。\n\n**本次待审核：**\n\n"
                for i, action in enumerate(actions):
                    name = action.get("name", "未知工具")
                    args_str = json.dumps(action.get("args", action.get("arguments", {})), ensure_ascii=False, indent=2)
                    interrupt_text += f"**{i+1}.** 工具：`{name}`  \n参数：\n```json\n{args_str}\n```\n\n"
                interrupt_text += "**请直接回复：** `同意` / `拒绝` / `编辑 N {参数}` / `退出` / `帮助`\n"
                history.append({"role": "assistant", "content": interrupt_text})
                return history

            else:
                history.append({"role": "assistant", "content": "未知状态，审核已结束"})
                current_interrupt_info = None
                return history

        except Exception as e:
            history.append({"role": "assistant", "content": f"审核执行异常：{str(e)}"})
            current_interrupt_info = None
            return history

    else:
        payload = {"user_id": USER_ID, "thread_id": THREAD_ID, "question": message}
        history.append({"role": "assistant", "content": "思考中..."})

        try:
            resp = requests.post(f"{BASE_URL}/ask", json=payload, timeout=90)

            if resp.status_code != 200:
                history[-1]["content"] = f"API 错误 {resp.status_code}: {resp.text}"
                return history

            data = resp.json()

            if data.get("status") == "completed":
                answer = data.get("result", "无返回内容").strip()
                history[-1]["content"] = answer
                return history

            elif data.get("status") == "interrupted":
                current_interrupt_info = data.get("interrupt_details", {})
                actions = current_interrupt_info.get("action_requests", [])
                interrupt_text = "\n**⚠️ 需要人工确认（安全审核）**\n\n**待审核的工具调用：**\n\n"
                for i, action in enumerate(actions):
                    name = action.get("name", "未知工具")
                    args_str = json.dumps(action.get("args", action.get("arguments", {})), ensure_ascii=False, indent=2)
                    interrupt_text += f"**{i+1}.** 工具：`{name}`  \n参数：\n```json\n{args_str}\n```\n\n"
                interrupt_text += "**请直接回复：** `同意` / `拒绝` / `编辑 N {参数}` / `退出` / `帮助`\n"
                history[-1]["content"] = interrupt_text
                return history

            else:
                history[-1]["content"] = "未知响应状态"
                return history

        except Exception as e:
            history[-1]["content"] = f"请求异常：{str(e)}"
            return history


# 清空对话并重置中断状态
def clear_chat():
    global current_interrupt_info
    current_interrupt_info = None
    return []


theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="gray",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont('Inter'), 'system-ui', 'sans-serif'],
)

custom_css = """
.gradio-container { max-width: 1400px !important; width: 1400px !important; margin: auto; padding: 1.5rem 3rem; background: #f8fafc; }
#chatbot { border-radius: 1rem; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04); background: white; }
.message { padding: 0.35rem 0.8rem !important; margin: 0.2rem 0 !important; border-radius: 1rem !important; max-width: 100% !important; font-size: 0.75rem !important; line-height: 1.25 !important; }
.user { background-color: #e0f2fe !important; margin-left: auto !important; margin-right: 0.3rem !important; border-radius: 1rem 1rem 0 1rem !important; }
.bot { background-color: #f1f5f9 !important; margin-right: auto !important; margin-left: 0.3rem !important; border-radius: 1rem 1rem 1rem 0 !important; }
.textbox { font-size: 0.75rem !important; border-radius: 0.75rem !important; border: 1px solid #cbd5e1 !important; }
.button { font-size: 0.75rem !important; padding: 0.5rem 1.2rem !important; }
.hint-text { font-size: 0.75rem !important; color: #9ca3af !important; text-align: left !important; margin-top: 0.25rem !important; margin-bottom: 1rem !important; margin-left: 0.5rem !important; line-height: 1.3; }
"""

# Gradio 使用不同端口
GRADIO_PORT = getattr(Config, "GRADIO_PORT", 7860)

# ────────────────────────────────────────────────
#             Gradio 界面
# ────────────────────────────────────────────────
with gr.Blocks(theme=theme, css=custom_css, title="Agent 对话测试（带 HITL + Skill）") as demo:
    gr.Markdown("# Agent 对话测试（带 HITL + Skill）")
    gr.Markdown(f"用户：`{USER_ID}`　｜　会话ID：`{THREAD_ID}`　｜　后端：`{BASE_URL}`")

    chatbot = gr.Chatbot(value=[], height=520, show_label=False, elem_id="chatbot")
    msg = gr.Textbox(placeholder="在这里输入您的问题或审核指令...", label="消息", lines=2, autofocus=True)
    # 提示信息紧挨输入框下方、左对齐
    gr.Markdown("提示：支持摘要、翻译等 Skill；出现工具审核时回复「同意」「拒绝」「编辑 N {参数}」「退出」「帮助」", elem_classes="hint-text")

    with gr.Row():
        send_btn = gr.Button("发送", variant="primary", scale=2)
        clear_btn = gr.Button("清空对话", variant="secondary", scale=1)

    # 交互逻辑：发送后清空输入框
    send_btn.click(fn=send_message, inputs=[msg, chatbot], outputs=chatbot).then(fn=lambda: "", inputs=None, outputs=msg)
    clear_btn.click(clear_chat, outputs=chatbot)


if __name__ == "__main__":
    print(f"启动 Gradio 界面... FastAPI 后端地址：{BASE_URL}")
    print(f"当前会话 thread_id: {THREAD_ID}\n")
    print("审核提示：支持 '同意' '拒绝' '编辑 N {JSON}' '退出' '帮助'；本版本支持 Skill（摘要、翻译）\n")

    demo.launch(
        server_name="127.0.0.1",
        server_port=GRADIO_PORT,
        theme=theme,
        inbrowser=True,
        share=False
    )
