import os
import logging
import argparse
import sys

from ghastoolkit.octokit.dependencygraph import DependencyGraph
from ghastoolkit.octokit.github import GitHub

from cdsa import __name__ as name
from cdsa.syft import Syft

logger = logging.getLogger(name)
parser = argparse.ArgumentParser(name)

parser.add_argument("-c", "--container", type=str)
parser.add_argument("-d", "--dockerfile", type=str)

parser.add_argument("--debug", action="store_true", help="Debug mode")
parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA"), help="Commit SHA")
parser.add_argument("--ref", default=os.environ.get("GITHUB_REF"), help="Commit ref")

parser_github = parser.add_argument_group("GitHub")
parser_github.add_argument(
    "-gr",
    "--github-repository",
    default=os.environ.get("GITHUB_REPOSITORY"),
    help="GitHub Repository",
)
parser_github.add_argument(
    "-gi",
    "--github-instance",
    default=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
    help="GitHub Instance",
)
parser_github.add_argument(
    "-t",
    "-gt",
    "--github-token",
    default=os.environ.get("GITHUB_TOKEN"),
    help="GitHub API Token",
)


if __name__ == "__main__":
    arguments = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG
        if arguments.debug or os.environ.get("DEBUG")
        else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    GitHub.init(arguments.github_repository, reference=arguments.ref)
    logging.info(f"Repository :: {GitHub.repository}")

    depgraph = DependencyGraph()

    syft = Syft()

    if not syft.check():
        syft.install()

    logging.debug(f"Syft Path :: {syft.binary}")

    sbom = None

    if arguments.container:
        logging.info("In container mode...")

        logging.info(f"Starting SBOM generation")
        sbom = syft.generateSBOM(arguments.container)

    elif arguments.dockerfile:
        logging.info("In Dockerfile mode")
        logging.warning(
            "This mode automatically builds the docker image which can have issues"
        )

        name = syft.buildContainer(arguments.dockerfile)

        sbom = syft.generateSBOM(name)

        for manifest, data in sbom.get("manifests", {}).items():
            data["file"] = {"source_location": arguments.dockerfile}
            sbom["manifests"][manifest] = data

    if sbom:
        logging.info("Uploading SBOM...")

        depgraph.submitSbom(sbom)

    else:
        logging.error("Failed to generate SBOM!")
        sys.exit(1)

    logging.info("Completed")
