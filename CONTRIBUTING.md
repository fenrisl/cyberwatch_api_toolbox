### Process to push a new version on PyPi (Python Package Index) with Github Actions

## Setup the package version

In the file `setup.py` configure the new version:

```python
...
long_description_content_type="text/markdown",
version='2.0.1',
author='CyberWatch SAS',
...
```

Commit the change, push to your Git repository remote on GitHub, create a pull request into the `master` branch.
Once the pull request is merged, the final steps are:

- Create a new release with the same version at https://github.com/Cyberwatch/cyberwatch_api_toolbox/releases
- Once created, a Github Action workflow will launch and upload the new version to PyPI

