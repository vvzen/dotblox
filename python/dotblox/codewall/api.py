import os
import shutil
from PySide2 import QtWidgets


DEBUG = False


ARCHIVE_FOLDER_NAME = "__archive"

def run_file(file_path):
    import pymel.core as pm

    if os.path.isfile(file_path):
        if file_path.endswith(".py"):
            pm.evalDeferred(
                    "with open(\"{file_path}\") as f:\n"
                    "\texec (compile(f.read(), \"{file_path}\", 'exec'), globals(), locals())"
                    "".format(file_path=file_path))
        elif file_path.endswith(".mel"):
            pm.mel.eval('source \"{file_path}\"'.format(file_path=file_path))


def create_new_folder_dialog(path):
    new_folder, accepted = QtWidgets.QInputDialog.getText(
            None,
            "Code Wall: New Folder",
            "Folder Name:")

    # canceled
    if not accepted:
        return False

    if new_folder == "":
        QtWidgets.QMessageBox.information(None,
                                          "Code Wall: Invalid",
                                          "No name Specified.")
        return create_new_folder_dialog(path)

    new_path = os.path.join(path, new_folder)

    if os.path.exists(new_path):
        QtWidgets.QMessageBox.information(None,
                                          "Code Wall: Invalid",
                                          "Folder already exists!")
        return create_new_folder_dialog(path)

    if DEBUG:
        print("Creating new folder " + new_path)
        return True

    os.mkdir(new_path)
    return True


def script_dialog(root_path):
    script_editor.build(root_path, edit=os.path.isfile(root_path))


def rename_dialog(file_path):
    full_name = os.path.basename(file_path)
    name, ext = os.path.splitext(full_name)

    parent_dir = os.path.dirname(file_path)

    def redo(default_text=None):
        new_name, accepted = QtWidgets.QInputDialog.getText(
                None,
                "Code Wall: Rename {name}".format(
                        name=full_name if default_text is None else default_text),
                "New Name:",
                QtWidgets.QLineEdit.Normal,
                os.path.basename(name))

        if not accepted:
            return False

        if new_name == "":
            QtWidgets.QMessageBox.information(None,
                                              "Code Wall: Invalid",
                                              "No Name specified")
            return redo(new_name)

        new_path = os.path.join(parent_dir, new_name)

        if os.path.exists(new_path):
            QtWidgets.QMessageBox.information(None,
                                              "Code Wall: Invalid",
                                              "Path already exists!")
            return redo(new_name)

        if DEBUG:
            print "Renaming {src} to {dst}".format(src=file_path, dst=new_path)
            return True
        os.rename(file_path, new_path)
        return True

    redo()


def remove(file_path, archive_root=None):
    dialog = QtWidgets.QMessageBox(None,
                                   "Code Wall: Delete",
                                   "Are you sure you want to delete {name}".format(
                                           name=os.path.basename(file_path)))
    if archive_root is not None:
        archive = dialog.addButton("Archive", QtWidgets.QMessageBox.AcceptRole)
    delete = dialog.addButton("Delete", QtWidgets.QMessageBox.DestructiveRole)
    cancel = dialog.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
    dialog.exec_()

    clicked_button = dialog.clickedButton()

    if clicked_button == cancel:
        return False

    if archive_root is not None and clicked_button == archive:
        archive_path = os.path.join(archive_root, ARCHIVE_FOLDER_NAME)

        if DEBUG:
            print ("Archiving {path} to {archive_path}".format(
                    path=file_path,
                    archive_path=archive_path))
            return True

        if not os.path.exists(archive_path):
            os.mkdir(archive_path)
        shutil.move(file_path, os.path.join(archive_path, os.path.basename(file_path)))

    if clicked_button == delete:
        if DEBUG:
            print ("Deleting {path}".format(path=file_path))
            return True

        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)

        return True

    return False
