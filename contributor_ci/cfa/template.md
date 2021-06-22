---
repository: {{ repository }}
title: {{ repository }}
---

# Contributor Friendliness Assessment for {{ repository }}

The Contributor Friendliness Assessment (CFA) makes an effort to assess a software project
for contributor friendliness.

{% for name, attrs in items.items() %}
## {{ name }}
{% for criteria in attrs.criteria %}
 {% if criteria.met %}- [x]{% else %}- [ ]{% endif %} {{ criteria.name }}{% if criteria.metric %}: {{ criteria.metric }}{% endif %}{% endfor %}
{% endfor %}
