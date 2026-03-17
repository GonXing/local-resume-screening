# 本地简历筛选工具

这个仓库只保留一套极简本地流程：

1. 你手动在 `resume/` 下创建一个批次文件夹
2. 把这一批简历放进去
3. 用本地 AI 提取结构化 JSON
4. 由本地 AI 继续运行 Python 评分脚本
5. 去 `output/` 看结果

你只需要操作两个目录：

- `resume/`
- `output/`

## 目录约定

输入目录：

- `resume/<批次名>/`

例如：

- `resume/spring-2026-01/`

你把这一批 PDF / DOCX / DOC 简历直接放进这个目录。

输出目录：

- `output/<批次名>/`

例如：

- `output/spring-2026-01/`

最终这里只保留：

- `ranking.csv`
- 每位候选人的评分 JSON，例如 `张三.json`

## 使用方式

### 1. 手动创建批次目录

例如新建：

```bash
mkdir -p resume/spring-2026-01
```

然后把这一批简历放进：

```bash
resume/spring-2026-01/
```

### 2. 用本地 AI 提取简历信息

把下面这份提示词发给本地 AI 工具：

- [prompts/local_resume_batch_prompt.md](/Users/jasin/python/remote/prompts/local_resume_batch_prompt.md)

你只需要把其中的 `{{batch_name}}` 替换成真实批次名，例如：

- `spring-2026-01`

提取结果会先写到：

- `output/<批次名>/.extracted/`

这是中间目录。本地 AI 在提取完成后还应继续执行：

```bash
python3 scripts/process_local_batch.py --batch-name <批次名>
```

评分完成后，这个中间目录会自动删除。

### 3. 运行评分

如果你给本地 AI 的提示词用的是当前仓库里的最新版，它会在提取后自动运行这一步。

如果你想手动补跑，也可以自己执行：

```bash
python3 scripts/process_local_batch.py --batch-name spring-2026-01
```

### 4. 查看结果

评分完成后，去这里看最终结果：

- `output/spring-2026-01/`

会看到：

- `ranking.csv`
- `候选人姓名.json`

## 保留文件

核心文件只有这些：

- [README.md](/Users/jasin/python/remote/README.md)
- [resume/README.md](/Users/jasin/python/remote/resume/README.md)
- [output/README.md](/Users/jasin/python/remote/output/README.md)
- [prompts/local_resume_batch_prompt.md](/Users/jasin/python/remote/prompts/local_resume_batch_prompt.md)
- [rules/recruiting_rules.json](/Users/jasin/python/remote/rules/recruiting_rules.json)
- [scripts/process_local_batch.py](/Users/jasin/python/remote/scripts/process_local_batch.py)
- [scripts/batch_score_resumes.py](/Users/jasin/python/remote/scripts/batch_score_resumes.py)
- [scripts/score_resume.py](/Users/jasin/python/remote/scripts/score_resume.py)

## 说明

- 这个仓库不包含飞书、OpenClaw 服务器、cron、云盘下载
- 它只负责本地批量评分流程
- 不同面试官只要拉取仓库，就能在自己电脑上按相同规则复用
