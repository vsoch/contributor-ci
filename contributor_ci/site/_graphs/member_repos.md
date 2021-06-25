---
layout: graph
title: Member Repositories
---

<svg id="members"></svg>
<svg id="pie_repos"></svg>

<script src="{{ site.baseurl }}/assets/js/extractors/member_repos.js"></script>
<script src="{{ site.baseurl }}/assets/js/extractors/pie_repos.js"></script>

<script>
$(document).ready(function(){
  draw_pie_users('#members');
  draw_pie_repos('#pie_repos');
})
</script>
