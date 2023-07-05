import os
import pyperclip

from Qt import QtCore, QtWidgets, QtGui
from dcc.ui import quicwindow

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class QEzResourceBrowser(quicwindow.QUicWindow):
    """
    Overload of QUicWindow used to browse icons within the current environment.
    """

    # region Dunderscores
    __extensions__ = ('.png', '.ico', '.svg', '.bmp', '.cur')

    def __init__(self, *args, **kwargs):
        """
        Private method called after a new instance has been created.

        :key parent: QtWidgets.QWidget
        :key flags: QtCore.Qt.WindowFlags
        :rtype: None
        """

        # Call parent method
        #
        super(QEzResourceBrowser, self).__init__(*args, **kwargs)

        # Declare public variables
        #
        self.searchLineEdit = None
        self.resourceTableView = None
        self.resourceItemModel = None  # type: QtGui.QStandardItemModel
        self.resourceItemFilterModel = None  # type: QtCore.QSortFilterProxyModel

        self.customContextMenu = None  # type: QtWidgets.QMenu
        self.copyAction = None  # type: QtWidgets.QAction
        self.exportAction = None  # type: QtWidgets.QAction
    # endregion

    # region Methods
    def postLoad(self, *args, **kwargs):
        """
        Called after the user interface has been loaded.

        :rtype: None
        """

        # Call parent method
        #
        super(QEzResourceBrowser, self).postLoad(*args, **kwargs)

        # Create standard item model
        #
        self.resourceItemModel = QtGui.QStandardItemModel(0, 1, parent=self.resourceTableView)
        self.resourceItemModel.setObjectName('resourceItemModel')

        self.resourceItemFilterModel = QtCore.QSortFilterProxyModel(parent=self.resourceTableView)
        self.resourceItemFilterModel.setSourceModel(self.resourceItemModel)

        self.resourceTableView.setModel(self.resourceItemFilterModel)

        # Create custom context menu
        #
        self.customContextMenu = QtWidgets.QMenu('', parent=self.resourceTableView)
        self.customContextMenu.setObjectName('customContextMenu')

        self.copyAction = QtWidgets.QAction('&Copy Resource', self.customContextMenu)
        self.copyAction.setObjectName('copyAction')
        self.copyAction.triggered.connect(self.on_copyAction_triggered)

        self.exportAction = QtWidgets.QAction('&Export Resource', self.customContextMenu)
        self.exportAction.setObjectName('exportAction')
        self.exportAction.triggered.connect(self.on_exportAction_triggered)

        self.customContextMenu.addActions([self.copyAction, self.exportAction])

        # Invalidate item model
        #
        self.invalidate()

    def currentItem(self):
        """
        Returns the current item.

        :rtype: QtGui.QStandardItem
        """

        selectionModel = self.resourceTableView.selectionModel()
        index = self.resourceItemFilterModel.mapToSource(selectionModel.currentIndex())

        return self.resourceItemModel.itemFromIndex(index)

    def invalidate(self):
        """
        Re-populates the item model with the latest resources.

        :rtype: None
        """

        # Reset row count
        #
        self.resourceItemModel.setRowCount(0)

        # Iterate through resource paths
        #
        iterDirs = QtCore.QDirIterator(":", QtCore.QDirIterator.Subdirectories)

        while iterDirs.hasNext():

            # Check if this is an image
            #
            resourcePath = iterDirs.next()
            filename = os.path.basename(resourcePath)
            name, extension = os.path.splitext(filename)

            if extension not in self.__extensions__:

                continue

            # Append row to item model
            #
            item1 = QtGui.QStandardItem(QtGui.QIcon(resourcePath), resourcePath)
            self.resourceItemModel.appendRow([item1])
    # endregion

    # region Slots
    @QtCore.Slot()
    def on_searchLineEdit_editingFinished(self):
        """
        Editing finished slot method responsible for invalidating the item filter model.

        :rtype: None
        """

        pattern = '*{text}*'.format(text=self.sender().text())

        self.resourceItemFilterModel.setFilterWildcard(pattern)
        self.resourceItemFilterModel.invalidateFilter()

    @QtCore.Slot(QtCore.QPoint)
    def on_resourceTableView_customContextMenuRequested(self, point):
        """
        Custom context menu requested slot method responsible for displaying the actions menu.

        :type point: QtCore.QPoint
        :rtype: None
        """

        self.customContextMenu.exec_(self.sender().mapToGlobal(point))

    @QtCore.Slot(bool)
    def on_copyAction_triggered(self, checked=False):
        """
        Triggered slot method responsible for copying the selected item to the clipboard.

        :type checked: bool
        :rtype: None
        """

        pyperclip.copy(self.currentItem().text())

    @QtCore.Slot(bool)
    def on_exportAction_triggered(self, checked=False):
        """
        Triggered slot method responsible for exporting the selected item.

        :type checked: bool
        :rtype: None
        """

        # Get current resource
        #
        currentItem = self.currentItem()
        resourcePath = currentItem.text()

        filename = os.path.basename(resourcePath)
        name, extension = os.path.splitext(filename)

        # Prompt user for save path
        #
        savePath, accepted = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption="Save Image Resource - {name}".format(name=name),
            filter="Images (*{extension})".format(extension=extension)
        )

        if accepted:

            log.info('Saving resource to: %s' % savePath)
            QtGui.QPixmap(resourcePath).save(savePath, format=extension[1:], quality=100)

        else:

            log.info('Operation aborted...')
    # endregion
