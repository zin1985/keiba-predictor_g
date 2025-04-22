import os
import datetime
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
USED_RACES_FILE = "used_races.json"

def generate_post():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")
    year_month = now.strftime("%Y-%m")

    if os.path.exists(USED_RACES_FILE):
        with open(USED_RACES_FILE, "r", encoding="utf-8") as f:
            used_races = json.load(f)
    else:
        used_races = []

    used_race_prompts = ", ".join([f"{r['year_month']}の{r['race']}" for r in used_races])
    avoid_instruction = f"以下のレースは既に生成済みのため、同じレース名・年月の組み合わせは避けてください: {used_race_prompts}"

    prompt = f"""
あなたは競馬評論家AIです。以下の条件に基づき、将来のG1競馬レースについて、SEOに強く、読み応えのある日本語ブログ記事を生成してください。

条件：
- 記事タイトルにレース名を含めてください（例：「2025年春天皇賞 - 王者の座を巡る決戦」）
- 既に使ったレース名＋年月（{used_race_prompts}）は避けてください
- 各セクションは400字以上
- 全体で5000字以上
- 表形式（馬一覧など）や図解風の構成があれば優先的に使ってください
- 各馬の情報は表形式でまとめる
- ペース予想・展開予想など図式的に表現できる所はなるべく図式的に表現（例：逃げ→先行→差し→追い込み）
- 出走馬一覧、オッズ表、予想の表などを表形式にしてください。
- 根拠の情報も分かりやすくリンクを付けてください。
※架空のレース、出走馬、レースプログラムは禁止です。

構成例：
1. レース概要
2. 出走馬と注目点（表形式）
3. 過去との比較
4. 馬場・天候の影響
5. 世間の予想とオッズ
6. 展開予想（図解形式でもOK）
7. 最終予想：◎本命、○対抗、▲穴馬
8. AI考察と理由
9. 編集後記

{avoid_instruction}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }

    response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception("Gemini API error:", response.text)

    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    lines = text.split("\n")
    first_line = lines[0].replace("#", "").strip()
    body = "\n".join(lines[1:]).strip()

    if any(r for r in used_races if r["race"] == first_line and r["year_month"] == year_month):
        print("$26A0$FE0F 同じレースが既に生成されているためスキップします")
        return

    filename = f"_posts/{date_str}-{time_str}-g1-predict.md"
    os.makedirs("_posts", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""---
title: "{first_line}"
date: {date_str}
layout: post
description: "AIによる競馬G1予想と展開分析"
---

{body}
""")

    used_races.append({"race": first_line, "year_month": year_month})
    with open(USED_RACES_FILE, "w", encoding="utf-8") as f:
        json.dump(used_races, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    generate_post()
