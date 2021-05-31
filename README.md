# Contributor CI

![docs/assets/img/contributor-ci.png](docs/assets/img/contributor-ci.png)

[![GitHub Marketplace](https://img.shields.io/static/v1?label=Marketplace&message=contributor-action&color=blue?style=flat&logo=github)](https://github.com/marketplace/actions/contributor-ci-action)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](https://github.com/vsoch/contributor-ci-action/blob/master/LICENSE)

**under development**

## Usage

**coming soon**

### contributor-action

A GitHub action to collect temporal metrics about the number of internal and
external contributors to your organization. You might be interested in using
this if you are starting a campaign to improve participation.

#### 1. repos.yaml

The one requirement you will need is a contributor-ci.yaml file, which is a configuration
file that include:

##### organizations

We need to know about member organizations (under which you can extract members and label them as internal
to your organization), and additional organizations that have member projects. 
You can see [contributor-ci.yaml](contributor-ci.yaml) for an example.

## TODO

 - should read in a contributor-ci.yaml file and require github token exported
 - write client that writes to a specified output directory
 - organized by content - should be repos, users, dates, etc.
 - contributor-action can be run to generate this data
 - contributor friendliness assessment should discover a new repo, if a file doesn't exist, open a PR

