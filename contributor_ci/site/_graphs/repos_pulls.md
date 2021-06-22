---
layout: graph
title: Repository Pulls
---

<svg id="repos_pulls"></svg>
<script src="{{ site.baseurl }}/assets/js/extractors/repos_pulls.js"></script>

<script>
$(document).ready(function(){
  draw_scatter_repo_pulls('#repos_pulls');
})
</script>
