#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_competition_name(competition, rules):
    raw_name = competition.get("name", "") or ""
    normalized_name = competition.get("normalized_name", raw_name) or raw_name
    aliases = rules.get("competition_aliases", {})

    for alias, target in aliases.items():
        if alias.lower() in raw_name.lower() or alias.lower() in normalized_name.lower():
            return target

    return normalized_name


def gpa_band_score(gpa):
    if gpa is None:
        return 0, [], ["缺少GPA证据"]
    if gpa >= 3.9:
        return 24, ["GPA表现突出"], []
    if gpa >= 3.7:
        return 21, ["GPA较强"], []
    if gpa >= 3.5:
        return 17, [], []
    if gpa >= 3.2:
        return 12, [], []
    return 7, [], ["GPA竞争力一般"]


def rank_bonus(rank_percent):
    if rank_percent is None:
        return 0, [], []

    if rank_percent <= 5:
        return 8, ["排名前5%，有明显加分"], []
    elif rank_percent <= 10:
        return 7, ["排名前10%，有较强加分"], []
    return 0, [], ["排名未进入前10%，排名项无加分"]


def academic_score(candidate):
    strengths = []
    risks = []
    gpa = candidate.get("gpa")
    rank_percent = candidate.get("rank_percent")

    if gpa is not None:
        gpa_score, gpa_strengths, gpa_risks = gpa_band_score(gpa)
        rank_score, rank_strengths, rank_risks = rank_bonus(rank_percent)
        score = gpa_score + rank_score
        strengths.extend(gpa_strengths + rank_strengths)
        risks.extend(gpa_risks + rank_risks)
    elif rank_percent is not None:
        rank_score, rank_strengths, rank_risks = rank_bonus(rank_percent)
        # Ranking alone should not dominate the academic dimension.
        score = 8 + rank_score
        strengths.extend(rank_strengths)
        risks.extend(["缺少GPA证据"] + rank_risks)
    else:
        score = 0
        risks.append("缺少GPA和排名证据")

    return clamp(score, 0, 35), strengths, risks


def scholarship_score(candidate, rules):
    hits = []
    total = 0
    strengths = []
    for scholarship in candidate.get("scholarships", []):
        name = scholarship.get("name", "")
        weight = rules["scholarship_weights"].get(name)
        if weight is None:
            continue
        total += weight
        hits.append({"name": name, "score": weight})
        strengths.append(f"获得{name}")

    return clamp(total, 0, 15), hits, strengths


def competition_score(candidate, rules):
    hits = []
    total = 0
    strengths = []
    risks = []

    for competition in candidate.get("competitions", []):
        raw_name = competition.get("name", "")
        normalized = normalize_competition_name(competition, rules)
        tier = rules["competition_tiers"].get(normalized, "UNKNOWN")
        tier_score = rules["competition_tier_scores"].get(tier, 1)
        award = competition.get("award", "")
        boosted_score = tier_score
        if any(keyword in award for keyword in ("冠军", "金奖", "一等奖", "特等奖", "S奖")):
            boosted_score += 2
        elif any(keyword in award for keyword in ("二等奖", "银奖", "全国前200")):
            boosted_score += 1

        total += boosted_score
        hits.append(
            {
                "raw_name": raw_name,
                "normalized_name": normalized,
                "tier": tier,
                "award": award,
                "score": boosted_score,
            }
        )
        if tier == "A":
            strengths.append(f"A档竞赛经历：{normalized}")
        elif tier == "UNKNOWN":
            risks.append(f"竞赛含金量待确认：{raw_name}")

    return clamp(total, 0, 25), hits, strengths, risks


def is_relevant_experience_text(text):
    text = text.lower()
    return any(
        keyword in text
        for keyword in (
            "quant",
            "量化",
            "ai",
            "python",
            "data",
            "research",
            "machine learning",
            "回测",
            "金融科技",
            "人工智能",
            "算法",
            "统计",
        )
    )


def is_research_item(project):
    text = " ".join(str(project.get(field, "")) for field in ("name", "summary")).lower()
    return any(
        keyword in text
        for keyword in ("research", "科研", "论文", "课题", "实验室", "发表", "导师", "项目研究")
    )


def internship_project_score(candidate, rules):
    internships = candidate.get("internships", [])
    projects = candidate.get("projects", [])
    score = 0
    strengths = []
    risks = []
    research_count = 0

    for internship in internships:
        text = " ".join(
            str(internship.get(field, "")) for field in ("company", "role", "summary")
        )
        if is_relevant_experience_text(text):
            score += rules["experience_scoring"]["relevant_internship"]
        else:
            score += rules["experience_scoring"]["general_internship"]

    for project in projects:
        text = " ".join(str(project.get(field, "")) for field in ("name", "summary"))
        if is_relevant_experience_text(text):
            score += rules["experience_scoring"]["relevant_project"]
        else:
            score += rules["experience_scoring"]["general_project"]
        if is_research_item(project):
            research_count += 1

    if internships or projects:
        strengths.append(f"有{len(internships)}段实习/科研经历和{len(projects)}个项目")
    else:
        risks.append("缺少实习和项目经历")

    if len(internships) >= 2:
        strengths.append("实习经历数量较多")
    elif len(internships) == 0:
        risks.append("缺少实习经历")

    if research_count > 0:
        research_bonus = min(
            research_count * rules["experience_scoring"]["research_bonus_per_item"],
            rules["experience_scoring"]["research_bonus_cap"],
        )
        score += research_bonus
        strengths.append(f"有{research_count}段科研相关经历")
    else:
        risks.append("科研经历证据较少")

    return clamp(score, 0, 15), strengths, risks


def fit_score(candidate, rules):
    score = 0
    keywords = rules["fit_keywords"]
    texts = []

    for field in ("skills", "motivation"):
        value = candidate.get(field, [])
        if isinstance(value, list):
            texts.extend(value)
        elif value:
            texts.append(value)

    for item in candidate.get("projects", []):
        texts.append(item.get("summary", ""))
        texts.append(item.get("name", ""))

    combined = " ".join(str(text).lower() for text in texts)
    high_hits = [term for term in keywords["high_value"] if term.lower() in combined]
    medium_hits = [term for term in keywords["medium_value"] if term.lower() in combined]

    score += min(len(high_hits) * 2, 8)
    score += min(len(medium_hits), 2)

    strengths = []
    risks = []

    if high_hits:
        strengths.append("与AI/量化/金融科技方向匹配度较高")
    else:
        risks.append("社团方向匹配证据不足")

    return clamp(score, 0, 10), high_hits, medium_hits, strengths, risks


def decision(total_score, thresholds):
    if total_score >= thresholds["interview"]:
        return "interview"
    if total_score >= thresholds["hold"]:
        return "hold"
    return "reject"


def followup_questions(result):
    questions = []
    if not result["competition_tier_hits"]:
        questions.append("你是否参加过AI、量化、数学或编程相关竞赛？")
    if "社团方向匹配证据不足" in result["risks"]:
        questions.append("你为什么想加入金融科技、AI、量化方向的学术社团？")
    if any("待确认" in risk for risk in result["risks"]):
        questions.append("请补充竞赛级别、奖项和你在团队中的具体职责。")
    if not questions:
        questions.append("请具体介绍你最能体现AI、量化或金融科技能力的一段经历。")
    return questions[:3]


def review_resume(candidate, rules):
    result = {
        "candidate_name": candidate.get("name", ""),
        "strengths": [],
        "risks": [],
    }

    acad_score, acad_strengths, acad_risks = academic_score(candidate)
    sch_score, sch_hits, sch_strengths = scholarship_score(candidate, rules)
    comp_score, comp_hits, comp_strengths, comp_risks = competition_score(candidate, rules)
    exp_score, exp_strengths, exp_risks = internship_project_score(candidate, rules)
    fit_pts, high_hits, medium_hits, fit_strengths, fit_risks = fit_score(candidate, rules)

    total_score = acad_score + sch_score + comp_score + exp_score + fit_pts

    result.update(
        {
            "academic_score": acad_score,
            "scholarship_score": sch_score,
            "competition_score": comp_score,
            "internship_project_score": exp_score,
            "fit_score": fit_pts,
            "total_score": total_score,
            "competition_tier_hits": comp_hits,
            "scholarship_hits": sch_hits,
            "keyword_hits": {
                "high_value": high_hits,
                "medium_value": medium_hits,
            },
        }
    )

    result["strengths"].extend(acad_strengths + sch_strengths + comp_strengths + exp_strengths + fit_strengths)
    result["risks"].extend(acad_risks + comp_risks + exp_risks + fit_risks)
    result["decision"] = decision(total_score, rules["thresholds"])
    result["followup_questions"] = followup_questions(result)

    return result


def main():
    parser = argparse.ArgumentParser(description="Score a student resume against club recruiting rules.")
    parser.add_argument("input", help="Path to candidate JSON")
    parser.add_argument(
        "--rules",
        default="rules/recruiting_rules.json",
        help="Path to recruiting rules JSON",
    )
    args = parser.parse_args()

    candidate = load_json(args.input)
    rules = load_json(args.rules)
    result = review_resume(candidate, rules)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
