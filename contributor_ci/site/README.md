# Contributor CI

This is a [contributor-ci](https://github.com/vsoch/contributor-ci) site generated to show metrics about GitHub
contributions. You can update the data with:

```bash
$ pip install contributor-ci
$ cci ui update
```

or generate your own site as follows:

```bash
$ pip install contributor-ci
$ mkdir -p my-cci
$ cd my-cci

# Any of the following work!
$ cci init user:vsoch
$ cci init org:spack
$ cci ui --cfa generate
```
