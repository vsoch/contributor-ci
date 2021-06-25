---
layout: page
title: Welcome
category: home
description: Welcome to a Contributor CI Graph Portal
permalink: /
---

# {{ page.title }}

**contributor ci** is a <a href="https://contributor-ci.readthedocs.io" target="_blank">library for extracting contributor metadata</a> and then visualizing the data and providing an interface to keep track of project contributor friendliness. This is the visualization portal.
{:.larger.text}

We invite you to explore the following visualizations:

{% include ordered_child_list.liquid docs=site.graphs %}

{% if site.cfa.size > 0 %}
Or explore the <a href="{{ site.baseurl }}/cfa/">Contributor Friendliness Assessment</a>.{% endif %}
