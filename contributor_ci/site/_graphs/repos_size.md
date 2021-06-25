---
layout: graph
title: Repository Sizes
heading: Popular Repositories
---

<svg id="repos_size"></svg>
<script src="{{ site.baseurl }}/assets/js/extractors/repos_size.js"></script>

<script>
$(document).ready(function(){
  repos_sizes('#repos_size');
})
</script>
