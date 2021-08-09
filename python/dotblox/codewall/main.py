import os
import subprocess

from PySide2 import QtWidgets, QtCore, QtGui

from dotblox.codewall.ui.fileviewwidget import FileViewWidget
from dotblox.icon import get_icon


class CodeWallWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        widget_title = "Code Wall"
        self.setObjectName(widget_title.lower().replace(" ", "_"))
        self.setWindowTitle(widget_title)

        self.ui = CodeWallUI()
        self.ui.setup_ui(self)

        self.ui.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        tab_bar = self.ui.tab_widget.tabBar()  # type: QtWidgets.QTabBar
        tab_bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self.tab_bar_context_menu)

        self.populate_tabs()

    def populate_tabs(self):
        for i in range(self.ui.tab_widget.count()):
            self.ui.tab_widget.removeTab(i)

        # tab = FileViewWidget(os.path.expanduser("~/Desktop"))
        # self.ui.tab_widget.addTab(tab, tab.tab_name(depth=1))

        tab = FileViewWidget(os.path.expanduser("~/Desktop"))
        self.ui.tab_widget.addTab(tab, "A")
        tab = FileViewWidget(os.path.expanduser("~/Desktop"))
        self.ui.tab_widget.addTab(tab, "B")
        tab = FileViewWidget(os.path.expanduser("~/Desktop"))
        self.ui.tab_widget.addTab(tab, "C")

    def _on_tab_close_requested(self, index):
        widget = self.ui.tab_widget.widget(index)
        result = QtWidgets.QMessageBox.question(
                None,
                "Code Wall: Close Tab",
                "Are you sure you want to close {}.\n"
                "This will permanently remove it from the settings.".format(
                        widget.root_path))
        if result == QtWidgets.QMessageBox.No:
            return

        self.ui.tab_widget.removeTab(index)

    def tab_bar_context_menu(self, pos):
        tab_bar = self.ui.tab_widget.tabBar()  # type: QtWidgets.QTabBar

        index = tab_bar.tabAt(pos)
        widget = self.ui.tab_widget.widget(index)

        def open_in_system(file_path):
            if hasattr(os, "startfile"):
                os.startfile(file_path.replace("/", "\\"))
            else:
                subprocess.call(["open", file_path])

        menu = QtWidgets.QMenu()
        menu.addAction("Show In Explorer", lambda *x: open_in_system(widget.root_path))
        menu.exec_(QtGui.QCursor.pos())


class CodeWallUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setSpacing(2)

        self.menu_bar = QtWidgets.QMenuBar(parent)
        main_layout.setMenuBar(self.menu_bar)

        self.menu_btn = QtWidgets.QPushButton()
        self.menu_btn.setIcon(QtGui.QIcon(get_icon("dblx_menu.png")))
        self.menu_btn.setStyleSheet("""
           QPushButton{
               background-color: transparent;
               outline:none;
               border:none;
           }

           QPushButton::menu-indicator {
               image: none;
               }
           """)

        self.menu_bar.setCornerWidget(self.menu_btn, QtCore.Qt.TopRightCorner)
        self.menu_bar.setNativeMenuBar(False)

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)

        self.tab_widget.setMovable(True)
        main_layout.addWidget(self.tab_widget)

        self.settings_menu = QtWidgets.QMenu("Settings Menu")
        local_menu = self.settings_menu.addMenu("Add Local Path")
        self.explore_menu_local_menu = local_menu.addAction("Explore")
        self.script_dir_local_menu = local_menu.addAction("Maya Script Dir")
        self.default_local_menu = local_menu.addAction("Default")

        global_Menu = self.settings_menu.addMenu("Add Global Path")
        self.explore_menu_global_menu = global_Menu.addAction("Explore")
        self.script_dir_global_menu = global_Menu.addAction("Maya Script Dir")

        self.menu_btn.setMenu(self.settings_menu)

        parent.setLayout(main_layout)
