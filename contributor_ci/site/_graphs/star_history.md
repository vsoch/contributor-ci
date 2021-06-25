---
layout: graph
title: Repository Star History
---

<svg id="star_history"></svg>
<script src="{{ site.baseurl }}/assets/js/extractors/star_history.js"></script>

<script>
$(document).ready(function(){
  draw_line_repo_star_history('#star_history');
})
</script>
