import os
import json
import glob
import tempfile
import logging
import subprocess

logger = logging.getLogger("cdsa.syft")

LOCATIONS = [
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
]
LOCATIONS.extend(glob.glob("/home/linuxbrew/.linuxbrew/Cellar/syft/**/bin"))


class Syft:
    def __init__(self) -> None:
        self.name = "syft"
        self.path = None

    @property
    def binary(self) -> str:
        if self.path:
            return os.path.join(self.path, self.name)
        return self.name

    def try_command(self, cmd: list[str]) -> bool:
        try:
            with open(os.devnull, "w") as null:
                subprocess.check_call(cmd, stdout=null, stderr=null)
            return True
        except:
            logger.debug("Syft not found on the system")
        return False

    def check(self) -> bool:
        for loc in LOCATIONS:
            logger.debug(f"Checking location :: {loc}")

            fullpath = os.path.join(loc, "syft")

            if os.path.exists(fullpath) or self.try_command([fullpath]):
                self.path = loc
                return True
        return False

    def install(self):
        """Install syft via Brew"""
        # https://github.com/actions/runner-images/blob/main/images/linux/Ubuntu2204-Readme.md#package-management
        # https://github.com/anchore/syft#homebrew
        logger.info("Installing syft via brew")
        cmd = ["/home/linuxbrew/.linuxbrew/bin/brew", "install", "syft"]
        subprocess.run(cmd, check=True)

        logger.info("Finished installing!")

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
