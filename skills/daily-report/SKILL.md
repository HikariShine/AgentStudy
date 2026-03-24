---
name: daily-report
description: Generate daily work report for ShineClaw project.
homepage: https://github.com/openclaw/openclaw
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "requires": { "bins": [] },
      },
  }
---

# Daily Report Generator

Generate daily work report based on memory files and session history.

## Usage

```bash
# Generate today's daily report
# This will output the report content for preview first
# Then commit and push after user confirmation
```

## Workflow

1. **读取记忆**：扫描 `memory/` 目录下的当日文件
2. **汇总信息**：整理完成的工作事项
3. **汇总明日待办**（重点）：
   - 读取当日 `memory/YYYY-MM-DD.md` 的待办章节，标记未完成项目（`[ ]`）
   - 扫描当日聊天记录，提取所有标记为"明日待办"或"明日 Task"的内容
   - 合并上述两项，去重后作为明日待办列表
4. **生成日报**：输出 Markdown 格式的日报到 `reports/YYYY-MM-DD.md`
5. **预览确认**：先展示内容给用户，不直接提交
6. **提交推送**：用户确认后，执行 Git add → commit → push

## Report Structure

```markdown
# 工作日报 - YYYY-MM-DD (详细版)

**日期**：YYYY-MM-DD (周X)  
**记录人**：ShineClaw  
**主题**：[填写今日核心主题]

---

## 📋 今日完成事项

### 1. ✅ [模块名/任务名] (Deep Dive/实操记录)
*   **背景/目标**：...
*   **详细操作**：...
*   **关键发现/效果**：...

### 2. ✅ [其他事项]
*   ...

---

## 🕵️ 关键发现与源码缺陷 (Patch/审计参考)
1.  **[缺陷点1]**：[详细描述，包含文件路径、逻辑问题、复现现象]
2.  ...

---

## 📊 今日数据统计
| 维度 | 详细数据 | 备注 |
| :--- | :--- | :--- |
| Git 提交 | ... | ... |
| AIGC 产出 | ... | ... |
| 缺陷诊断 | ... | ... |

---

## 🔜 明日待办 (YYYY-MM-DD)
1.  **[任务1] (Priority: High)**：...
2.  ...

---

## 📎 参考资料
*   ...

---
*由 ShineClaw 汇总生成于 YYYY-MM-DD HH:MM*
```

## Content Guidelines

- **尽可能详细**：不要只写“修复了 Bug”，要写清楚修复的具体逻辑、操作步骤和代码层面的改动。
- **深度溯源**：如果发现了源码缺陷，必须记录详细的文件路径和逻辑缺陷，为后续 Patch 提供参考。
- **存储规范**：如果涉及 AIGC 生成，需提及文件流转路径（Workspace -> 附件库）及 README 登记情况。
- **关联记忆**：利用 `memory/` 下的详细日志进行内容扩充，还原实战细节。
- **数据化**：尽可能使用表格统计今日的工作产出。

## Output Location

- Report file: `${HOME}/projects/shineclaw/reports/YYYY-MM-DD.md`
- Must follow existing report format in `reports/` directory