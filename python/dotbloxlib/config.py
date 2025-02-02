import copy
import json
import os
import sys


class ConfigIO(object):
    def __init__(self, file_path, read, write, default=None, sync=False):
        """File IO class for contextual reading and writing of a
        configuration file

        Args:
            file_path (str): file path to the config file
            read (func): the function used when reading the file
            write (func): the function to use when writing the file
            default (dict): the default data to cache when the file
                            doesnt exist.
            sync (bool): when data is read the latest is pulled from the file.
                         when data is written the file is updated on disk.

        Usage:
            io = ConfigIO(file_path, read, write)
            with io as data:
                current_data = data

            with io.write() as data:
                data["key"] = value

        """
        self.file_path = file_path
        self.modified_time = 0
        self.__context_write = False
        self._sync = False
        self._io_read = read
        self._io_write = write

        if default is None:
            default = {}

        self.cache = {}
        self.default_data = default

    def save_to_disk(self):
        try:
            with open(self.file_path, "w") as f:
                self._io_write(f, self.cache)
        except:
            print("Unable to save to " + self.file_path)

    def read_from_disk(self, force=False):
        """Read the file from disk.

        This checks the modified time of the file as to avoid subsequent
        reads

        Args:
            force (bool): forces a read from disk even if the modified
                           time is the same

        Returns:
            dict: data from the configuration
        """
        if not os.path.exists(self.file_path):
            self.cache = copy.copy(self.default_data)
            return

        last_modified = os.path.getmtime(self.file_path)
        if self.modified_time < last_modified or force:
            self.modified_time = last_modified
            with open(self.file_path, "r") as f:
                self.cache = self._io_read(f)

    def __enter__(self):
        if self._sync:
            self.read_from_disk()
        return self.cache

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__context_write and self._sync:
            self.save_to_disk()

    def write(self):
        """Use in a with statement to auto save the file when sync is on"""
        self.__context_write = True
        return self

    def pause_sync(self):
        """Pause syncing"""
        self._sync = False

    def start_sync(self, save=False):
        """Start sync and save current to file if given

        Args:
            save (bool): save the file when stating the syc

        """
        self._sync = True
        if save:
            self.save_to_disk()


class BaseConfig(object):
    def __init__(self, path, default=None):
        """Base class for config files.

        _io_read and io_write must be implemented in subsequent classes

        Args:
            path (str): the fie path of the config
            default (dict): default data to fill the file
        """
        self.io = ConfigIO(path, self._io_read, self._io_write, default=default)
        self.io.read_from_disk()

    def _io_read(self, f):
        """The function to be used when reading the file

        Args:
            f (file): the file object passed through

        Returns:
            dict: the data to be cached
        """
        raise NotImplementedError("%s._io_read must be implented" % self.__class__.__name__)

    def _io_write(self, f, data):
        """The function to be used when writing the file

        Args:
            f (file): the file object passed through
        """
        raise NotImplementedError("%s._io_write must be implented" % self.__class__.__name__)

    def pause_sync(self):
        """Pause the io syncing"""
        self.io.pause_sync()

    def is_paused(self):
        """Check is io is syncing with changes"""
        return not self.io._sync

    def start_sync(self, save=False):
        """Start syncing with file changes"""
        self.io.start_sync(save=save)

    def save(self):
        """Save current contents to disk"""
        self.io.save_to_disk()

    def __eq__(self, other):
        return self.io.file_path == other or self != other

    def revert(self):
        """Revert the file from the current contents on disk"""
        self.io.read_from_disk(force=True)


class ConfigJSON(BaseConfig):
    def __init__(self, path, default=None):
        """Base Class for reading and writing a json file

        This class is meant to be inherited.

        Usage:
            class Settings(ConfigJSON):
                def get_data(self):
                    with self.io as data:
                        return data
                def set_data(self, data)
                    with self.io.write() as data:
                        data.update(data)

        """
        BaseConfig.__init__(self, path, default)

    def _io_read(self, f):
        return json.load(f)

    def _io_write(self, f, data):
        json.dump(data, f, indent=4)


def _path_find_generator(name):
    """Search for a config given the file name along sys.path

    Args:
        name (str): exact file name to search for

    Returns:
        generator: generator object holding the paths
    """
    seen = []
    for path in sys.path:
        # Sanitize paths just in case
        path = path.replace("\\", '/')
        # In case sys.path has multiples and has different slashes in the path
        if path in seen:
            continue
        seen.append(path)

        config_path = os.path.join(path, name)
        config_path = config_path.replace("\\", '/')
        if not os.path.exists(config_path):
            continue

        yield config_path


def find_all(name):
    """Find all configs with the given name along sys.path

    Args:
        name (str): Name of file including the extension
    """
    return list(_path_find_generator(name))


def find_one(name):
    """Find the first config with the given name along sys.path

    Args:
        name (str): Name of file including the extension
    """
    try:
        return next(_path_find_generator(name))
    except StopIteration:
        return None
