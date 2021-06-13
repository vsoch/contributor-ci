__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from contributor_ci.logger import logger
import contributor_ci.defaults as defaults
import contributor_ci.main.schemas
import contributor_ci.utils

from datetime import datetime
import jsonschema
import os


class SettingsBase:
    def __init__(self):
        """
        Create a new settings object not requiring a settings file.
        """
        # Set an updated time, in case it's written back to file
        self._settings = {"updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        self.settings_file = None

    def __str__(self):
        return "[contributor-ci-settings]"

    def __repr__(self):
        return self.__str__()

    def validate(self):
        """
        Validate the loaded settings with jsonschema
        """
        jsonschema.validate(
            instance=self._settings, schema=contributor_ci.main.schemas.config_schema
        )

    def load(self, settings_file=None):
        """
        Load the settings file into the settings object
        """
        self.settings_file = settings_file or defaults.default_settings_file

        # Exit quickly if the settings file does not exist
        if not os.path.exists(self.settings_file):
            logger.exit("%s does not exist." % self.settings_file)

        # Load the yaml file into settings
        self._settings = contributor_ci.utils.read_yaml(self.settings_file)

    def add(self, key, value):
        """
        Given an existing key and a value, add the value to the list.
        """
        current = self.get(key)
        if not current:
            logger.exit("%s is not a known key to add to." % key)
        if not isinstance(current, list):
            logger.exit("You can only remove from a setting key that is a list.")
        logger.info("Adding %s to %s" % (value, key))
        current.append(value)
        current = sorted(list(set(current)))
        self.set(key, current)

    def remove(self, key, value):
        """
        Given an existing key and a value, remove the value.
        """
        current = self.get(key)
        if not current:
            logger.exit("%s is not a known key to remove from." % key)
        if not isinstance(current, list):
            logger.exit("You can only remove from a setting key that is a list.")
        current = set(current)
        if value not in current:
            logger.exit("%s is not in %s." % (value, key))
        logger.info("Removing %s from %s" % (value, key))
        current.remove(value)
        current = sorted(list(current))
        self.set(key, current)

    def sort(self):
        """
        Sort all lists.
        """
        for key, value in self._settings.items():
            if isinstance(value, list):
                value.sort()

    def get(self, key, default=None):
        value = self._settings.get(key, default)
        return self._substitutions(value)

    def __getattr__(self, key):
        """
        A direct get of an attribute, but default to None if doesn't exist
        """
        return self.get(key)

    def edit(self):
        """
        Interactively edit a config file.
        """
        editor = self.editor or "vim"
        if not self.settings_file or not os.path.exists(self.settings_file):
            logger.exit("Settings file not found.")
        contributor_ci.utils.run_command([editor, self.settings_file], stream=True)

    def set(self, key, value):
        """
        Set a setting based on key and value. If the key has :, it's nested
        """
        value = True if value == "true" else value
        value = False if value == "false" else value

        # This is a reference to a dictionary (object) setting
        if ":" in key:
            key, subkey = key.split(":")
            self._settings[key][subkey] = value
        else:
            self._settings[key] = value

    def _substitutions(self, value):
        """
        Given a value, make substitutions
        """
        if isinstance(value, bool) or not value:
            return value

        # Currently dicts only support boolean or null so we return as is
        elif isinstance(value, dict):
            return value

        for rep, repvalue in defaults.reps.items():
            if isinstance(value, list):
                value = [x.replace(rep, repvalue) for x in value]
            else:
                value = value.replace(rep, repvalue)

        return value

    def delete(self, key):
        if key in self._settings:
            del self._settings[key]

    def save(self, filename=None):
        filename = filename or self.settings_file
        if not filename:
            logger.exit("A filename is required to save to.")
        contributor_ci.utils.write_yaml(self._settings, filename)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value


class Settings(SettingsBase):
    """
    The settings class is a wrapper for easily parsing a settings.yml file.

    We parse into a query-able class. It also gives us control to update settings,
    meaning we change the values and then write them to file. It's basically
    a dictionary-like class with extra functions.
    """

    def __init__(self, settings_file):
        """
        Create a new settings object, which requires a settings file to load
        """
        self.load(settings_file)
        self.validate()
