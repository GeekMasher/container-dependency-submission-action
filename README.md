# container-dependency-submission-action

Container Dependency Submission API Action 

## Requirements

- Python 3.9+
- [Syft](https://github.com/anchore/syft)
- [optional] Homebrew
  - Used to dynamically install syft

## Usage

```yaml
- name: Conatiner Dependency Submission Action
  uses: GeekMasher/container-dependency-submission-action@main
  with:
    # requires either "container" or "dockerfile" to be set
    container: "container-name:latest"
    # or 
    dockerfile: "Dockerfile"
```

### Action Inputs


```yaml
- name: Conatiner Dependency Submission Action
  uses: GeekMasher/container-dependency-submission-action@main
  with:
    # `conatiner` is the name of the container already built on the system
    container: "container-name:latest"

    # `dockerfile` is the path to the Dockerfile that defined the container image 
    # which is then built
    dockerfile: "Dockerfile"
    
    # [optional ] Token used to authenticate with the GitHub API. Defaults to the GITHUB_TOKEN secret.
    token: ${{ secrets.CODEQL_SUMMARY_GENERATOR_TOKEN }}
```


### Workflow Example

```yaml
name: Conatiner Dependency Submission Action
on:
  push:
    branches: [main]

permissions: 
  contents: write   # needed

jobs:
  gradle-lock:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      # ... build your conatiner 

      - name: Gradle Lock Dependency Submission Action
        uses: GeekMasher/container-dependency-submission-action@main
        with:
          container: "container-name:latest" 
```

## License 

This project is licensed under the terms of the MIT open source license. Please refer to [MIT](./LICENSE) for the full terms.


## Maintainers 

Maintained by [@GeekMasher](https://github.com/GeekMasher).


## Support

Please create GitHub Issues and Discussions for any feature requests, bugs, or documentation problems.


## Acknowledgement

- @GeekMasher: Author and Maintainer



