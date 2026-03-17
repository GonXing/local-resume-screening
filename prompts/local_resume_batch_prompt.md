# Local Resume Batch Prompt

把这份提示词发给本地 AI 助手使用，例如 `Codex`、`Claude Code` 或 `antigravity`。

用途：

- 本地读取 `resume/<批次名>/` 中的 PDF / Word 简历
- 提取结构化 JSON
- 写入 `output/<批次名>/.extracted/`
- 然后运行本地评分脚本
- 最终结果保留在 `output/<批次名>/`

## 可直接复制的模板

把下面这段直接发给本地 AI，把 `spring-2026-01` 替换成你的真实批次名即可。

```text
你在处理一个本地简历审批批次。你的任务分两步：
1. 从本地简历文件中提取结构化 JSON
2. 提取完成后运行 Python 评分脚本，生成最终结果

本次批次名：spring-2026-01

不要做这些事：
- 不要修改 Python 规则文件
- 不要生成 CSV、Markdown、DOCX
- 不要安装新依赖，除非环境里已经有成熟可用的 PDF / DOCX 读取方式
- 不要输出冗长的中间思考过程
- 不要只告诉用户“接下来运行什么命令”，你必须自己执行该命令

你必须遵守以下目录约定：
- 原始简历目录：resume/spring-2026-01
- 提取结果目录：output/spring-2026-01/.extracted

执行目标：
1. 读取 `resume/spring-2026-01/` 下的所有 PDF / DOCX / DOC 简历
2. 对每一份简历生成一个 JSON 文件
3. JSON 文件写入 `output/spring-2026-01/.extracted/`
4. 一个简历对应一个 JSON 文件，文件名与原文件同名，仅扩展名改为 `.json`
5. 确认 JSON 全部写入后，执行：
   `python3 scripts/process_local_batch.py --batch-name spring-2026-01`
6. 评分完成后，最终结果应位于：
   `output/spring-2026-01/`
7. 你必须验证以下文件已经实际生成：
   - `output/spring-2026-01/ranking.csv`
   - 至少一个以候选人姓名命名的 JSON 文件

JSON 结构必须严格保持为：
{
  "name": "",
  "school": "",
  "major": "",
  "grade": "",
  "gpa": null,
  "rank": "",
  "rank_percent": null,
  "scholarships": [
    {
      "name": "",
      "raw_line": ""
    }
  ],
  "competitions": [
    {
      "name": "",
      "normalized_name": "",
      "award": "",
      "raw_line": ""
    }
  ],
  "internships": [
    {
      "company": "",
      "role": "",
      "summary": ""
    }
  ],
  "projects": [
    {
      "name": "",
      "summary": ""
    }
  ],
  "skills": [],
  "english": [],
  "motivation": "",
  "evidence_notes": []
}

提取原则：
1. 只提取有明确证据的信息，不要臆造
2. 不确定的信息留空、填 null 或空数组
3. 比赛和奖学金名称尽量映射到标准名
4. 如果无法可靠映射，就保留原始名称，并把 normalized_name 设为原始名称

奖学金标准名称：
- 国家奖学金
- 国家励志奖学金
- 校级甲等奖学金 (一等)
- 校级乙等奖学金 (二等)
- 校级丙等奖学金 (三等)
- 光华学子综合素质50强
- 单项奖学金 (科研/创新等)

竞赛标准名称：
- 美国大学生数学建模竞赛 (MCM/ICM)
- 全国大学生数学建模竞赛 (CUMCM)
- 全国大学生统计建模大赛
- CFA协会全球投资分析大赛 (CFA Research Challenge)
- 罗特曼国际交易大赛 (Rotman)
- ACM-ICPC 国际大学生程序设计竞赛
- “成都 80”金融科技设计与开发大赛
- 中国国际大学生创新大赛 (原互联网+)
- “挑战杯”全国大学生课外学术科技作品竞赛
- 中国高校计算机大赛-人工智能创意赛
- 蓝桥杯全国软件和信息技术专业人才大赛
- “工行杯”全国大学生金融科技创新大赛
- “东方财富杯”全国大学生金融挑战赛
- 全国大学生数学竞赛 (CMC)
- GMC 全球管理挑战赛
- “正大杯”全国大学生市场调查与分析大赛
- 中国大学生计算机设计大赛
- 招商银行数字金融训练营
- Kaggle 数据建模竞赛
- 校级金融模拟交易赛
- 院级案例分析大赛

完成标准：
- `output/spring-2026-01/.extracted/` 中每份简历都有对应 JSON
- 不要覆盖成空文件
- 必须继续运行评分脚本，不能停在提取阶段
- 必须亲自执行评分脚本，不能只给出命令建议
- 只有确认 `output/spring-2026-01/ranking.csv` 已存在后，才算完成
- 完成后只回复一句：处理完成
```

## 通用占位版

```text
你在处理一个本地简历审批批次。你的任务分两步：
1. 从本地简历文件中提取结构化 JSON
2. 提取完成后运行 Python 评分脚本，生成最终结果

不要做这些事：
- 不要修改 Python 规则文件
- 不要生成 CSV、Markdown、DOCX
- 不要安装新依赖，除非环境里已经有成熟可用的 PDF / DOCX 读取方式
- 不要输出冗长的中间思考过程
- 不要只告诉用户“接下来运行什么命令”，你必须自己执行该命令

你必须遵守以下目录约定：
- 批次名：{{batch_name}}
- 原始简历目录：resume/{{batch_name}}
- 提取结果目录：output/{{batch_name}}/.extracted

执行目标：
1. 读取 `resume/{{batch_name}}/` 下的所有 PDF / DOCX / DOC 简历
2. 对每一份简历生成一个 JSON 文件
3. JSON 文件写入 `output/{{batch_name}}/.extracted/`
4. 一个简历对应一个 JSON 文件，文件名与原文件同名，仅扩展名改为 `.json`
5. 确认 JSON 全部写入后，执行：
   `python3 scripts/process_local_batch.py --batch-name {{batch_name}}`
6. 评分完成后，最终结果应位于：
   `output/{{batch_name}}/`
7. 你必须验证以下文件已经实际生成：
   - `output/{{batch_name}}/ranking.csv`
   - 至少一个以候选人姓名命名的 JSON 文件

JSON 结构必须严格保持为：
{
  "name": "",
  "school": "",
  "major": "",
  "grade": "",
  "gpa": null,
  "rank": "",
  "rank_percent": null,
  "scholarships": [
    {
      "name": "",
      "raw_line": ""
    }
  ],
  "competitions": [
    {
      "name": "",
      "normalized_name": "",
      "award": "",
      "raw_line": ""
    }
  ],
  "internships": [
    {
      "company": "",
      "role": "",
      "summary": ""
    }
  ],
  "projects": [
    {
      "name": "",
      "summary": ""
    }
  ],
  "skills": [],
  "english": [],
  "motivation": "",
  "evidence_notes": []
}

提取原则：
1. 只提取有明确证据的信息，不要臆造
2. 不确定的信息留空、填 null 或空数组
3. 比赛和奖学金名称尽量映射到以下标准名
4. 如果无法可靠映射，就保留原始名称，并把 normalized_name 设为原始名称

奖学金标准名称：
- 国家奖学金
- 国家励志奖学金
- 校级甲等奖学金 (一等)
- 校级乙等奖学金 (二等)
- 校级丙等奖学金 (三等)
- 光华学子综合素质50强
- 单项奖学金 (科研/创新等)

竞赛标准名称：
- 美国大学生数学建模竞赛 (MCM/ICM)
- 全国大学生数学建模竞赛 (CUMCM)
- 全国大学生统计建模大赛
- CFA协会全球投资分析大赛 (CFA Research Challenge)
- 罗特曼国际交易大赛 (Rotman)
- ACM-ICPC 国际大学生程序设计竞赛
- “成都 80”金融科技设计与开发大赛
- 中国国际大学生创新大赛 (原互联网+)
- “挑战杯”全国大学生课外学术科技作品竞赛
- 中国高校计算机大赛-人工智能创意赛
- 蓝桥杯全国软件和信息技术专业人才大赛
- “工行杯”全国大学生金融科技创新大赛
- “东方财富杯”全国大学生金融挑战赛
- 全国大学生数学竞赛 (CMC)
- GMC 全球管理挑战赛
- “正大杯”全国大学生市场调查与分析大赛
- 中国大学生计算机设计大赛
- 招商银行数字金融训练营
- Kaggle 数据建模竞赛
- 校级金融模拟交易赛
- 院级案例分析大赛

完成标准：
- `output/{{batch_name}}/.extracted/` 中每份简历都有对应 JSON
- 不要覆盖成空文件
- 必须继续运行评分脚本，不能停在提取阶段
- 必须亲自执行评分脚本，不能只给出命令建议
- 只有确认 `output/{{batch_name}}/ranking.csv` 已存在后，才算完成
- 完成后只回复一句：处理完成
```
