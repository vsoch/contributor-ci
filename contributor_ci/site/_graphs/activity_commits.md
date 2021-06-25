---
layout: graph
title: Commit Activity
---

<svg id="repo_activity"></svg>
<script src="{{ site.baseurl }}/assets/js/extractors/activity_commits.js"></script>

<script>
$(document).ready(function(){
  draw_line_repo_activity('#repo_activity');
})
</script>
