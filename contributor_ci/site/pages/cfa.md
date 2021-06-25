---
layout: page
title: Contributor Friendliness Assessment
category: home
description: Welcome to a Contributor CI Graph Portal
permalink: /cfa/
---

# {{ page.title }}

**contributor ci** is a <a href="https://contributor-ci.readthedocs.io" target="_blank">library for extracting contributor metadata</a> and then visualizing the data and providing an interface to keep track of project contributor friendliness. This is the visualization portal for LLNL, which is under development.
{:.larger.text}

## The Contributor Friendliness Assessment

There are a lot of good projects out there that fail to attract contributors because
they aren't contributor friendly. What does it mean to be contributor friendly?
It means that your branding, resources, and associated tools make it easy to contribute.
By assessing the repositories of our organizations for contributor friendliness, we can
make it easier and more fun to contribute, and improve the overall health of the project.

More specifically, the Contributor Friendliness Assessment (CFA) is an effort to identify aspects of a repository that can be improved to make the repository more contributor friendly. The assessment derives a list of criteria to assess how easy it is to contribute to a project. This means arriving at a project repository and having an easy time going from knowing nothing to opening a pull request, and also how well the project attracts new contributors. Generally, we assess the repository for:

- **CFA-branding**: Does the project have branding?
- **CFA-popularity**: How popular is the project?
- **CFA-description**: Does the project have a clear description (What is it for)?
- **CFA-need**: Does the project have a compelling set of use cases, or statement of need (Should I use it)? This is a fork in the visitor’s decision tree, because if the answer is yes they will continue exploring, otherwise they will not.
- **CFA-license**: The GitHub repository has an OSI-approved open-source license.
- **CFA-build**: Methods to build or install the software or service are clearly stated.
- **CFA-examples**: Does the README.md have a quick example of usage?
- **CFA-documentation**: Does the project have documentation?
- **CFA-support**: Does the project make it easy to ask for help?
- **CFA-developer**: Process and metadata is provided for the developer to understand and make changes.
- **CFA-quality**: The code quality of the project.
- **CFA-tests**: The project has testing.
- **CFA-coverage**: The project reports code coverage.
- **CFA-format**: The project adheres to a language specific format.
- **CFA-outreach**: Is the project active at conferences or otherwise externally presented?

Most of these assessments are currently manual, and will be automated in time. You can read more about the CFA <a href="https://contributor-ci.readthedocs.io/en/latest/getting_started/user-guide.html#contributor-friendliness-assessment" target="_blank">here</a>, and we invite you to explore the following contributor friendliness assessments

<div class="ui bulleted link list" id="app">
</div>

This aspect of the interface is under development, so you can expect the design
of these pages to change. Return back to the <a href="{{ site.baseurl }}/">index here</a>.

<script>
function loadJSON(path, success, error)
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                if (success)
                    success(JSON.parse(xhr.responseText));
            } else {
                if (error)
                    error(xhr);
            }
        }
    };
    xhr.open("GET", path, true);
    xhr.send();
}


var colors = ["#B43C3C","#BB473E","#BF5340","#BF6240","#BF6F40","#BF7540","#BF7D40","#BF8440","#BF8E40","#BF9740","#BF9F40","#BFAA40","#BFB540","#BFBB40","#AEBF40","#9FBF40","#80BF40","#59BF40"];
var total = 47;

loadJSON('{{ site.baseurl }}/api/',
    function(data) {
    
      var items = [];
      $.each(data['data'], function(i, item) {
        console.log(item);
        // Prepare badge images
        var color_index = parseInt((item['checked'] / total) * colors.length)
        var badgeColor = colors[color_index];
        var score = (100 * (item['checked'] / total)).toFixed(2);
        var badgeScore = Math.round(score) + "%25"
        var badgeUrl = "https://img.shields.io/badge/software%20checklist-" + badgeScore + "-" + badgeColor.replace("#", "");
        $("#app").append( "<a href='"+ item['url'] + "' class='item' id='" + item['id'] + "'><img style='padding-right:15px' src='"+ badgeUrl + "'>" + item['id'] + "</a>" );
  }); 
    
    },
    function(xhr) { console.error(xhr); }
);

</script>
