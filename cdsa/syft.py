import os
import json
import tempfile
import logging
import subprocess

logger = logging.getLogger("cdsa.syft")

LOCATIONS = ["/usr/local/bin", os.path.expanduser("~/.local/bin")]


class Syft:
    def __init__(self) -> None:
        self.name = "syft"
        self.path = None

    @property
    def binary(self) -> str:
        if self.path:
            return self.path
        return self.name

    def check(self):
        for loc in LOCATIONS:
            fullpath = os.path.join(loc, "syft")
            if os.path.exists(fullpath):
                self.path = fullpath
                return True
        try:
            subprocess.check_call(self.binary)
            return True
        except:
            logger.debug("Syft not found on the system")
        return False

    def install(self):
        """Install syft via Brew"""
        # https://github.com/actions/runner-images/blob/main/images/linux/Ubuntu2204-Readme.md#package-management
        # https://github.com/anchore/syft#homebrew
        cmd = ["/home/linuxbrew/.linuxbrew/bin/brew", "install", "syft"]
        subprocess.run(cmd, check=True)

    def generateSBOM(self, image: str) -> dict:
        output = os.path.join(tempfile.gettempdir(), "syft-sbom.json")
        cmd = [self.binary, image, "-o", f"github-json={output}"]

        logger.debug(f"SBOM Command :: {cmd}")

        with open(os.devnull, "w") as null:
            subprocess.run(cmd, stdout=null, stderr=null)

        if os.path.exists(output):
            with open(output, "r") as handle:
                return json.load(handle)

        return {}

    def buildContainer(self, path: str) -> str:
        logger.info(f"Building container from path :: {path}")

        name = "cdsa-image:latest"
        cmd = ["docker", "build", "-t", name, "-f", path, os.getcwd()]

        logger.debug(f"Container Build Command :: `{cmd}`")

        subprocess.run(cmd, check=True)

        logger.info("Build command finished")
        return name
