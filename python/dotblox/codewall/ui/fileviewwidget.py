import os

from PySide2 import QtWidgets, QtCore, QtGui
from dotblox.codewall import api
from dotblox.icon import get_icon
# from .icon_event_filter import IconEventFilter


class FileViewWidget(QtWidgets.QWidget):
    def __init__(self, root_path=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.ui = FileViewWidgetUI()
        self.ui.setup_ui(self)

        self.file_system = FileSystemModel()
        self.file_system.setNameFilters(["*.py", "*.mel"])
        # self.file_system.setReadOnly(True)
        self.ui.tree_view.setModel(self.file_system)

        # self.ui.tree_view.customContextMenuRequested.connect(self.tree_view_context_menu)
        self.ui.tree_view.doubleClicked.connect(self._on_tree_view_double_click)

        self.ui.create_folder_btn.clicked.connect(self._on_create_folder)
        self.ui.create_script_btn.clicked.connect(self._on_create_script)

        # self.ui.tree_view.expanded.connect(self.store_state)
        # self.ui.tree_view.collapsed.connect(self.store_state)

        if root_path:
            self.set_root_path(root_path)
            # self.restore_state()

    def set_root_path(self, path):
        self.raw_root_path = path
        self.root_path = path
        self.file_system.setRootPath(self.root_path)
        self.ui.tree_view.setRootIndex(self.file_system.index(path))

    def _on_create_folder(self, folder_path=None):
        if folder_path is None:
            folder_path = self._get_selected_item_folder()

        api.create_new_folder_dialog(folder_path)

    def _on_create_script(self, folder_path=None):
        if folder_path is None:
            folder_path = self._get_selected_item_folder()
        api.script_dialog(folder_path)

    def _get_selected_item_folder(self):
        path = self.root_path
        selected = self.ui.tree_view.selectedIndexes()
        if selected:
            file_info = self.file_system.fileInfo(selected[0])  # type: QtCore.QFileInfo
            if file_info.isFile():
                path = file_info.path()
            else:
                path = file_info.filePath()

        return path

    def tree_view_context_menu(self, pos):
        index = self.ui.tree_view.indexAt(pos)  # type: QtCore.QModelIndex
        file_info = self.file_system.fileInfo(index)  # type: QtCore.QFileInfo
        file_path = file_info.filePath()  # type: str
        folder_path = file_path
        if file_info.isFile():
            folder_path = file_info.path()
        if not folder_path:
            folder_path = None

        menu = QtWidgets.QMenu(self)

        if file_info.isFile():
            menu.addAction("Run", lambda *x: self._run_file(file_path))

        new_item_menu = menu
        # Add "New:" items to a sub menu if the item is not the root
        if index.isValid():
            new_item_menu = menu.addMenu("New")  # type: QtWidgets.QMenu

        action = new_item_menu.addAction(
                "Folder",
                lambda *x: self._on_create_folder(folder_path=folder_path))
        action.setIcon(QtGui.QIcon(get_icon("dblx_folder.png")))
        action = new_item_menu.addAction(
                "Script",
                lambda *x: self._on_create_script(folder_path=folder_path))
        action.setIcon(QtGui.QIcon(get_icon("dblx_file.png")))

        edit_menu = menu.addMenu("Edit")  # type: QtWidgets.QMenu
        if not file_info.isDir():
            edit_menu.addAction("Modify", lambda *x: self._on_context_menu_modify_script(file_path))
        edit_menu.addAction("Rename", lambda *x: api.rename_dialog(file_path))
        edit_menu.addAction("Delete", lambda *x: api.remove(file_path, archive_root=self.root_path))

        menu.exec_(QtGui.QCursor.pos())

    def _on_tree_view_double_click(self, index):
        api.run_file(self.file_system.fileInfo(index).filePath())

    def _run_file(self, file_path):
        api.run_file(file_path)

    def _on_context_menu_modify_script(self, file_path):
        api.script_dialog(file_path)

    def tab_name(self, depth=1):
        path = self.root_path.replace("\\", "/")
        return "/".join(path.split("/")[-depth:])

    def store_state(self, index):
        path = self.file_system.fileInfo(index).filePath()
        item_path = path.replace(self.root_path, "").lstrip("/")
        if os.path.isdir(path):
            if self.ui.tree_view.isExpanded(index):
                config.state.set_state(self.raw_root_path, item_path)
            else:
                config.state.remove_state(self.raw_root_path, item_path)

    def restore_state(self):
        for path in config.state.get_states(self.raw_root_path):
            path = "{}/{}".format(self.root_path, path)
            if os.path.exists(path):
                print "expanding", path
                self.ui.tree_view.setExpanded(self.file_system.index(path), True)

    # def refresh(self):
    #     if self.rootPath.startswith("//"):
    #         selected = [self.fileSystem.filePath(x) for x in self.treeView.selectedIndexes()]
    #
    #
    #         self.fileSystem = WallFileSystemModel()
    #         self.fileSystem.setNameFilterDisables(False)
    #         self.fileSystem.setNameFilters(["*.py", "*.mel", self.archiveFolderName])
    #         self.treeView.setModel(self.fileSystem)
    #         self.treeView.setRootIndex(self.fileSystem.setRootPath(self.rootPath))
    #         self.restoreState()
    #
    #         for i in selected:
    #             self.treeView.setCurrentIndex(self.fileSystem.index(i))
    #


class FileViewWidgetUI():
    def setup_ui(self, parent_widget):
        # self.icon_event_filter = IconEventFilter()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)

        action_button_layout = QtWidgets.QHBoxLayout()
        action_button_layout.setContentsMargins(0, 0, 0, 0)
        # action_button_layout.setSpacing(2)

        self.create_folder_btn = QtWidgets.QPushButton()
        self.create_folder_btn.setIcon(QtGui.QIcon(get_icon("dblx_folder.png")))
        self.create_folder_btn.setStyleSheet("background-color: transparent;outline:none;border:none;")
        # self.create_folder_btn.installEventFilter(self.icon_event_filter)
        action_button_layout.addWidget(self.create_folder_btn)

        self.create_script_btn = QtWidgets.QPushButton()
        self.create_script_btn.setIcon(QtGui.QIcon(get_icon("dblx_file.png")))
        self.create_script_btn.setStyleSheet("background-color: transparent;outline:none;border:none;")
        # self.create_script_btn.installEventFilter(self.icon_event_filter)
        action_button_layout.addWidget(self.create_script_btn)

        main_layout.addLayout(action_button_layout)

        self.tree_view = _TreeView()
        self.tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_view.setHeaderHidden(True)

        main_layout.addWidget(self.tree_view)

        parent_widget.setLayout(main_layout)




class FileSystemModel(QtWidgets.QFileSystemModel):

    def __init__(self):
        QtWidgets.QFileSystemModel.__init__(self)
        # self.icon_provider = FileIconProvider()
        # self.setIconProvider(self.icon_provider)
        self.setNameFilterDisables(False)

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    def flags(self, index):
        """

        Args:
            index (QtCore.QModelIndex):

        Returns:

        """

        flags = QtWidgets.QFileSystemModel.flags(self, index)
        if self.isReadOnly():
            return flags

        flags |= QtCore.Qt.ItemIsDropEnabled

        if not index.isValid():
            return flags

        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsDragEnabled

        return flags

    def columnCount(self, index):
        """
            Set column count to 1

        Args:
            index (QtCore.QModelIndex):

        Returns:
            int

        """
        return 1

    def hasChildren(self, index):
        """
        Reimplemented:
            Remove arrow indicator on empty folders

        Args:
            index (QtCore.QModelIndex):
        """
        file_info = self.fileInfo(index)
        dir = file_info.dir()
        if dir.exists():
            if file_info.isDir():
                files = dir.entryList(self.nameFilters(),
                                      QtCore.QDir.AllDirs |
                                      QtCore.QDir.NoDotAndDotDot)
                return bool(files)
        return False

    def dropMimeData(self, data, action, row, column, parent):
        """

        Args:
            data (QtCore.QMimeData):
            action (QtCore.Qt.DropAction):
            row (int):
            column (int):
            parent (QtCore.QModelIndex):

        Returns:

        """
        if not data.hasUrls() \
                or (action & self.supportedDropActions()) == QtCore.Qt.IgnoreAction \
                or not parent.isValid() \
                or self.isReadOnly():
            return False


        parent_info = self.fileInfo(parent)  # type: QtCore.QFileInfo

        # filePath does some path resolving so use that to get the path
        dst_root = self.filePath(parent)
        if parent_info.isFile():
            dst_root = parent_info.path()
        dst_root += QtCore.QDir.separator()

        for url in data.urls():
            src_path = url.toLocalFile()
            dst_path = dst_root + QtCore.QFileInfo(src_path).fileName()
            if action == QtCore.Qt.CopyAction:
                QtCore.QFile.copy(src_path, dst_path)
            elif action == QtCore.Qt.MoveAction:
                QtCore.QFile.rename(src_path, dst_path)
        return True


class _TreeView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        QtWidgets.QTreeView.__init__(self, parent)

        self.setIconSize(QtCore.QSize(20, 20))
        self.setEditTriggers(self.SelectedClicked | self.EditKeyPressed)

        # Drag and Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDragDropMode(self.InternalMove)

    def mousePressEvent(self, event):
        """
        Reimplemented:
            Show the context menu on mouse down instead of mouse up
            Clear the selection if a click occurs out side of the list of items
        Args:
            event (QtGui.QMouseEvent):
        """

        if event.button() == QtCore.Qt.RightButton:
            QtWidgets.QTreeView.mousePressEvent(self, event)
            self.customContextMenuRequested.emit(event.pos())
        else:
            QtWidgets.QTreeView.mousePressEvent(self, event)

            index_under_mouse = self.indexAt(event.pos())
            if not index_under_mouse.isValid():
                self.clearSelection()
                return