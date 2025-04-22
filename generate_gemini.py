import os
import datetime
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"

def generate_post():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")

    prompt = f"""
あなたは競馬評論家AIです。以下の条件に基づき、近未来に開催されるG1レースについて、SEOに強く、読み応えのある日本語ブログ記事を生成してください。

【目的】
将来のG1競馬レースの開催情報、出走馬、調子、血統、馬場状態、天気、世間の予想を考慮し、
AIが独自に予想と展開解説を行う自動ブログを生成します。

【条件】
・各馬の情報は表形式でまとめる
・ペース予想・展開予想など図式的に表現できる所はなるべく図式的に表現（例：逃げ→先行→差し→追い込み）
・出走馬一覧、オッズ表、予想の表などを表形式にしてください。
・各セクションは400文字以上
・全体で5000文字以上
・事実とAIの考察を混ぜる構成にしてください
・根拠の情報も分かりやすくリンクを付けてください。

【構成】
1. レース名と開催情報
2. 出走予定馬とその注目ポイント
3. 過去の類似レースとの比較
4. 馬場状態や天気の影響
5. 世間の予想とオッズ傾向
6. AIによる展開予想（ペース、仕掛け、最終直線など）
7. AIの最終予想：◎本命、○対抗、▲穴馬
8. 考察：なぜその馬を本命としたか、データと感性の融合
9. 編集後記：レースへの期待や注目点

※Web上の情報を参考にした体裁で構いません。
※出走馬名・日付・レース名は実際にこれから開催される情報にしてください。架空のレース、馬、出走プログラムは禁止です。

"""

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096
        }
    }

    response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception("Gemini API error:", response.text)

    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    title = text.split("\n")[0].strip().replace("#", "").strip()
    body = "\n".join(text.split("\n")[1:]).strip()
    filename = f"_posts/{date_str}-{time_str}-g1-predict.md"

    os.makedirs("_posts", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""---
title: "{title}"
date: {date_str}
layout: post
description: "AIによる競馬G1予想。出走馬・オッズ・展開・馬場状態からの総合分析"
---

{body}
""")

if __name__ == "__main__":
    generate_post()
