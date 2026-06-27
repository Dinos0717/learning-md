---
name: transcript-to-doc
description: This skill should be used when the user provides a video transcript (逐字稿) and asks to convert it into a detailed teaching document (教学文档). Trigger phrases include: "生成教学文档", "写教案", "根据这个内容生成文档", "用相同的模版生成", "整理成教学文档", "把这个课程内容整理出来", "转化成详细文档", or any request to turn spoken/transcribed content into structured educational material. Also triggers when the user provides content labeled as "共享音频" (shared audio transcript) from 陈泽鹏 or similar course video transcripts.
version: 1.0.0
---

# 逐字稿教案转化（Transcript-to-Teaching-Document）

## Overview

This skill converts raw video course transcripts (逐字稿) into comprehensive, well-structured teaching documents (教学文档). It takes conversational, sometimes disorganized spoken content and transforms it into polished, logically-organized educational material suitable for student self-study.

## When to Use This Skill

Invoke this skill when:

- The user provides a block of video transcript text and asks to "生成文档", "写教案", "整理", etc.
- The user mentions "用相同的模版生成" (generate using the same template)
- Content is labeled with speaker names like "陈泽鹏 共享音频" and timestamps like "00:05"
- The user wants to create teaching material from course recordings
- The user asks to "详细" (add more detail) to an existing transcript-based document

## Conversion Principles

### Core Philosophy

The spoken transcript is the **raw material**. The teaching document is the **finished product**. The gap between them includes:

| Raw Transcript | → | Teaching Document |
|---|---|---|
| Conversational, repetitive | → | Concise, well-structured |
| Linear time-based flow | → | Logical chapter-based flow |
| Implicit knowledge | → | Explicit definitions and tables |
| Verbal emphasis ("注意!", "OK吧") | → | Visual emphasis (⚠️, tables, callouts) |
| Scattered code snippets | → | Complete, runnable code blocks |
| Informal examples | → | Systematic comparison tables |
| One-off mentions of errors | → | Organized troubleshooting guides |

### Key Rules

1. **Preserve all technical content** — Every concept, every code pattern, every warning the teacher mentions must appear in the document
2. **Remove verbal filler** — "Ok吧", "好", repetitive explanations of the same point, false starts
3. **Infer structure** — The teacher may not explicitly organize content into chapters; you must derive logical groupings
4. **Expand on concepts** — When the teacher mentions a term without defining it, add a brief definition
5. **Add visual organization** — Use tables, diagrams (ASCII art), callout boxes, and comparison charts
6. **Create navigability** — Always include a table of contents with anchor links
7. **Match the template style** — All documents in a series should share the same chapter structure and formatting patterns

## Document Template Structure

Every teaching document should follow this canonical structure. Not every section is required for every document; adapt based on the transcript content.

```
# [课程主题] (Title — derived from content, not transcript)

> 基于陈泽鹏老师视频课程整理编写 · [当前日期]

---

## 目录 (Table of Contents — always include, with anchor links)

---

## 一、课程背景与目标 (Background & Objectives)

### 1.1 前情回顾 (Previous Lesson Review)
- What was learned in the previous lesson
- Code recap from previous lesson (if applicable)

### 1.2 本节课的核心问题 (Core Problem)
- The problem scenario this lesson solves
- Presented as a question or problem table

### 1.3 本课要掌握的目标 (Learning Objectives)
- Visual box with numbered objectives
- Usually 2-3 key objectives derived from the teacher's opening remarks

---

## 二、[核心概念一] (First Core Concept)

### 2.1 直观理解 (Intuitive Understanding)
- Analogy or simple explanation
- "Before vs After" comparison if applicable

### 2.2 详细解释 (Detailed Explanation)
- Technical definition
- How it works

### 2.3 [子概念 / 子步骤] (Sub-concepts as needed)
- Break down complex topics into digestible chunks

---

## 三、[核心概念二] (Second Core Concept — if applicable)

(Following the same sub-structure as above)

---

## 四、实战演示 / 完整代码 (Hands-on / Complete Code)

### 4.1 完整代码
- Complete, runnable code block
- With comments in Chinese explaining each section

### 4.2 代码逐行解析 (Line-by-line Analysis)
- Table format: Line | Purpose | Details

---

## 五、[进阶内容] (Advanced Content — if applicable)

---

## 六、[对比与选择] (Comparison & Decision Guide — if applicable)
- Comparison tables for alternative approaches
- Decision trees

---

## 七、常见问题与排错指南 (Troubleshooting Guide)

### 7.1 错误速查表
| 错误信息 | 原因 | 解决方法 | 优先级 |

### 7.2 排查流程
- Step-by-step debugging flowchart (ASCII art)

---

## 八、课后练习 (Practice Exercises)

### 练习一: [基础练习]
### 练习二: [进阶练习]
### 练习三: [综合实战]
- Each with clear acceptance criteria
- Framework code hints where helpful

---

## 九、课程小结 (Lesson Summary)

### 9.1 核心知识图谱
- Visual box with all key knowledge points

### 9.2 一句话总结
- One-sentence takeaway

### 9.3 练习题答案 (if the transcript includes a quiz)
- Answer explanation with rationale for each option

### 9.4 系列课程定位
- Where this lesson fits in the overall curriculum

---

*本教学文档基于陈泽鹏老师视频课程整理编写。*
```

## Reusable Content Patterns

These patterns should appear consistently across all documents in the series:

### Pattern 1: Learning Objectives Box

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：[标题]                                   │
│         ├── [子目标1]                             │
│         ├── [子目标2]                             │
│         └── [子目标3]                             │
│                                                 │
│  目标二：[标题]                                   │
│         ├── [子目标1]                             │
│         └── [子目标2]                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Pattern 2: Before/After Comparison

```python
# ❌ Before (problem)
[code showing the problem]

# ✅ After (solution)
[code showing the solution]
```

### Pattern 3: Knowledge Graph Box (for summary chapter)

```
┌────────────────────────────────────────────────────────────┐
│               [Topic] 核心知识体系                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  [Key Point Title]                                     │
│      ├── [Detail 1]                                        │
│      ├── [Detail 2]                                        │
│      └── [Detail 3]                                        │
│                                                            │
│  2️⃣  [Key Point Title]                                     │
│      ...                                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Pattern 4: Process Flow Diagram

```
Step 1: [Action]
    ↓
Step 2: [Action]
    ↓
Step 3: [Action]
    ↓
🎉 Result
```

### Pattern 5: Decision Tree

```
Question?
    ├── Answer A → Action 1
    └── Answer B → Action 2
```

### Pattern 6: Series Positioning (always at the end)

```
第一课: [Title]
第二课: [Title]
...
第N课（本课）: [Title]  ← 你在这里
后续: [Future topics]
```

## Content Expansion Guidelines

When the transcript mentions something briefly, expand it appropriately:

| Transcript Mentions | Document Should Include |
|---|---|
| A code snippet shown on screen | Complete runnable code with comments, line-by-line analysis |
| An error the teacher encounters | Error name, cause, solution, a dedicated row in the troubleshooting table |
| "这个东西" / "那个东西" | The actual technical term with proper naming |
| A model/provider name | A row in a comparison table with all relevant attributes |
| Two alternative approaches | A full comparison table with pros/cons, use cases, code examples |
| "注意" / "一定要注意" | A ⚠️ callout box with prominent formatting |
| A quiz question at the end | The question, all options, correct answer with explanation |

## Code Block Standards

- All code blocks must be **complete and runnable** (include imports, API key setup)
- Add **Chinese comments** explaining each logical section
- Use `# ── Section Label ──` style separators for major sections
- Include both **simple** and **complete** versions when helpful
- Show **error-prone code** and **corrected code** side by side when relevant

## Table Usage Guidelines

Use tables liberally for:

- **Comparisons** (Method A vs Method B, Model X vs Model Y)
- **Parameter references** (all parameters with type, required/optional, description)
- **Error troubleshooting** (error → cause → solution)
- **Model/provider feature matrices**
- **Decision guides** (scenario → recommendation → reason)

## Tone and Language

- **Default language**: Chinese (Simplified)
- **Tone**: Professional but approachable, like a patient teacher
- **Use "你"** for the reader (not "您")
- **Use emoji** sparingly for visual cues (⚠️ for warnings, ✅/❌ for correct/incorrect, 🎉 for success)
- **Code comments**: Chinese
- **Technical terms**: Keep in English when standard (API, JSON, Python), explain in Chinese when first introduced

## Quality Checklist

Before finalizing any document, verify:

- [ ] Table of contents with working anchor links is included
- [ ] All code blocks are complete and have Chinese section comments
- [ ] At least one comparison table is present
- [ ] A troubleshooting/FAQ section exists (with error table if applicable)
- [ ] Practice exercises section has 3-5 exercises with clear criteria
- [ ] Knowledge graph box appears in the summary chapter
- [ ] Series positioning shows where this lesson fits
- [ ] All technical claims from the transcript are captured
- [ ] No verbal filler from the transcript remains
- [ ] ⚠️ callouts exist for every warning/note the teacher emphasized
- [ ] Document metadata line at the bottom (based on 陈泽鹏 video course)

## Handling "用相同的模版生成" Requests

When the user says "用相同的模版生成" followed by new transcript content:

1. Identify which existing document in the project is the "template" (usually the most recently created one)
2. Extract the **chapter structure pattern** from that template
3. Apply the same chapter organization to the new content
4. Match the **visual style** (same types of tables, same box styles, same code formatting)
5. Match the **depth of detail** (similarly comprehensive expansion)
6. Match the **auxiliary sections** (troubleshooting, exercises, summary format)
7. Ensure the new document can stand alone while fitting into the series

## Handling "能再详细一些吗" Requests

When the user asks to make an existing document more detailed:

1. Re-read the **original transcript** (not just the existing document)
2. Identify content that was mentioned but not fully expanded
3. Add depth in these dimensions:
   - More step-by-step breakdowns
   - Additional code examples (variants, edge cases)
   - More comparison tables
   - Line-by-line code analysis
   - Deeper conceptual explanations
   - More troubleshooting scenarios
   - Expanded practice exercises
4. Typically increases word count by 3-5x
