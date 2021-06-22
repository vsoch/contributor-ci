---
layout: graph
title: Repository Licenses
---

<svg id="licenses"></svg>
<script src="{{ site.baseurl }}/assets/js/extractors/licenses.js"></script>

<script>
$(document).ready(function(){
  draw_sunburst_licenses('#licenses');
})
</script>
