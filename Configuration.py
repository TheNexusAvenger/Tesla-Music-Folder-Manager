"""
TheNexusAvenger

Configuration for the Tesla file writer.
"""

import json
import re


class Configuration:
    def __init__(self, path: str):
        """Creates a configuration.

        :param path: Path of the configuration.
        """

        with open(path, encoding="utf8") as file:
            # Read the configuration.
            configuration = json.loads(file.read())

            # Throw an error if there are missing values.
            if "sourceDirectory" not in configuration.keys():
                raise KeyError("sourceDirectory not in configuration.")
            if "targetDirectory" not in configuration.keys():
                raise KeyError("sourceDirectory not in configuration.")

            # Store the values.
            self.sourceDirectory = configuration["sourceDirectory"]
            self.targetDirectory = configuration["targetDirectory"]
            if "fileWhitelist" in configuration.keys():
                self.fileWhitelist = configuration["fileWhitelist"]
            else:
                self.fileWhitelist = []
            if "fileBlacklist" in configuration.keys():
                self.fileBlacklist = configuration["fileBlacklist"]
            else:
                self.fileBlacklist = []
            if "extensionsWhitelist" in configuration.keys():
                for extension in configuration["extensionsWhitelist"]:
                    self.fileWhitelist.append("\\." + extension + "$")

    def fileBlacklisted(self, path) -> bool:
        """Returns if a path is blacklisted (matches at least 1 blacklist.

        :param path: Path to check.
        :return: Whether the path is allowed.
        """

        for blacklistEntry in self.fileBlacklist:
            if re.findall(blacklistEntry.lower(), path.lower().replace("\\", "/")):
                return True
        return False

    def fileAllowed(self, path: str) -> bool:
        """Returns if a file is allowed. It must pass all blacklists and at least one whitelist.

        :param path: Path to check.
        :return: Whether the path is allowed.
        """

        # Return false if a blacklist entry matches.
        if self.fileBlacklisted(path):
            return False

        # Return true if there is no whitelist or at least 1 entry matches.
        if len(self.fileWhitelist) == 0:
            return True
        for whitelistEntry in self.fileWhitelist:
            if re.findall(whitelistEntry.lower(), path.lower().replace("\\", "/")):
                return True

        # Return false (no whitelist entry matches).
        return False
