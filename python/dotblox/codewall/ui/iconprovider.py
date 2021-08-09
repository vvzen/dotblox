from PySide2 import QtWidgets, QtCore, QtGui
from ... import config


class FileIconProvider(QtWidgets.QFileIconProvider):
    def __init__(self):
        QtWidgets.QFileIconProvider.__init__(self)
        self.file = self.get_icon("file")
        self.folder = self.get_icon("folder")
        self.python = self.get_icon("python")
        self.mel = self.get_icon("mel")
        self.python_package = self.get_icon("pythonPackage")

    def icon(self, file_info, *args):

        if isinstance(file_info, QtCore.QFileInfo):
            path = file_info.filePath()

            if file_info.isFile():

                if file_info.suffix() in ["py", "pyc"]:
                    return self.python
                elif file_info.suffix() in ["mel"]:
                    return self.mel
                else:
                    return self.file
            else:
                if self._is_python_module(path):
                    return self.python_package
                else:
                    return self.folder

        return QtWidgets.QFileIconProvider.icon(self, file_info)

    def _is_python_module(self, path):
        return bool(QtCore.QDir(path).entryList(["__init__.*"]))

    def get_icon(self, name):
        icon_path = config.get_icon("fileTypes/{}.png".format(name))
        if icon_path:
            return QtGui.QPixmap(icon_path)
        else:
            return QtGui.QPixmap()
