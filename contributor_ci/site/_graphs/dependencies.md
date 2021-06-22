---
layout: graph
title: Repository Dependencies
---

<!-- Preset vis display areas -->
<center>
    <svg id="dependencies"></svg> <svg id="connectionsTree"></svg>
    <br /><form name="Keyword Search" onsubmit="searchForm(event)"><label>Search: </label><input id="search" type="text" placeholder="Type search term here&hellip;" spellcheck="false"></form>
</center>

<script src="{{ site.baseurl }}/assets/js/extractors/dependencies.js"></script>

<script>
$(document).ready(function(){
  draw_force_graph("#dependencies", "#connectionsTree");
})
</script>
