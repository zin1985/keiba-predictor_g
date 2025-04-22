---
layout: default
title: AI競馬予想ブログ
---

<h1>AIによるG1競馬予想</h1>

<ul>
  {% for post in site.posts %}
    <li><a href="{{ site.baseurl }}{{ post.url }}">{{ post.date | date: "%Y年%m月%d日" }} - {{ post.title }}</a></li>
  {% endfor %}
</ul>
