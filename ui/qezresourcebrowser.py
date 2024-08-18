import os

from Qt import QtCore, QtWidgets, QtGui
from dcc.ui import qsingletonwindow
from dcc.python import importutils
from ..libs import resourceutils

clipman = importutils.tryImport('clipman')

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class QEzResourceBrowser(qsingletonwindow.QSingletonWindow):
    """
    Overload of `QSingletonWindow` that can browse through resource icons.
    """

    # region Dunderscores
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

    def __post_init__(self, *args, **kwargs):
        """
        Private method called after an instance has initialized.

        :rtype: None
        """

        # Call parent method
        #
        super(QEzResourceBrowser, self).__post_init__(*args, **kwargs)

        # Invalidate user interface
        #
        self.invalidate()

    def __setup_ui__(self, *args, **kwargs):
        """
        Private method that initializes the user interface.

        :rtype: None
        """

        # Call parent method
        #
        super(QEzResourceBrowser, self).__setup_ui__(*args, **kwargs)

        # Initialize main window
        #
        self.setWindowTitle("|| Ez'Resource-Browser")
        self.setMinimumSize(QtCore.QSize(350, 450))

        # Initialize central widget
        #
        centralLayout = QtWidgets.QVBoxLayout()
        centralLayout.setObjectName('centralLayout')

        centralWidget = QtWidgets.QWidget()
        centralWidget.setObjectName('centralWidget')
        centralWidget.setLayout(centralLayout)

        self.setCentralWidget(centralWidget)

        # Initialize search line-edit
        #
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.searchLineEdit.setObjectName('searchLineEdit')
        self.searchLineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.searchLineEdit.setFixedHeight(24)
        self.searchLineEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.searchLineEdit.setPlaceholderText('Search...')
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.textChanged.connect(self.on_searchLineEdit_textChanged)

        centralLayout.addWidget(self.searchLineEdit)

        # Initialize resource table-view
        #
        self.resourceTableView = QtWidgets.QTableView()
        self.resourceTableView.setObjectName('resourceTableView')
        self.resourceTableView.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.resourceTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.resourceTableView.setStyleSheet('QTreeView::item { height = 24 };')
        self.resourceTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.resourceTableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.resourceTableView.setAlternatingRowColors(True)
        self.resourceTableView.setShowGrid(True)
        self.resourceTableView.setWordWrap(False)
        self.resourceTableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.resourceTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.resourceTableView.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.resourceTableView.customContextMenuRequested.connect(self.on_resourceTableView_customContextMenuRequested)

        self.resourceItemModel = QtGui.QStandardItemModel(0, 1, parent=self.resourceTableView)
        self.resourceItemModel.setObjectName('resourceItemModel')

        self.resourceItemFilterModel = QtCore.QSortFilterProxyModel(parent=self.resourceTableView)
        self.resourceItemFilterModel.setObjectName('resourceItemFilterModel')
        self.resourceItemFilterModel.setSourceModel(self.resourceItemModel)

        self.resourceTableView.setModel(self.resourceItemFilterModel)

        horizontalHeader = self.resourceTableView.horizontalHeader()  # type: QtWidgets.QHeaderView
        horizontalHeader.setStretchLastSection(True)
        horizontalHeader.setVisible(False)

        verticalHeader = self.resourceTableView.verticalHeader()  # type: QtWidgets.QHeaderView
        verticalHeader.setStretchLastSection(False)
        verticalHeader.setVisible(False)

        centralLayout.addWidget(self.resourceTableView)

        # Initialize custom context-menu
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
    # endregion

    # region Methods
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
        for resourcePath in resourceutils.iterIcons():

            # Append row to item model
            #
            item1 = QtGui.QStandardItem(QtGui.QIcon(resourcePath), resourcePath)
            self.resourceItemModel.appendRow([item1])
    # endregion

    # region Slots
    @QtCore.Slot(str)
    def on_searchLineEdit_textChanged(self, text):
        """
        Slot method for the `searchLineEdit` widget's `editingFinished` signal.

        :type text: str
        :rtype: None
        """

        pattern = '*{text}*'.format(text=text)

        self.resourceItemFilterModel.setFilterWildcard(pattern)
        self.resourceItemFilterModel.invalidateFilter()

    @QtCore.Slot(QtCore.QPoint)
    def on_resourceTableView_customContextMenuRequested(self, point):
        """
        Slot method for the `resourceTableView` widget's `customContextMenuRequested` signal.

        :type point: QtCore.QPoint
        :rtype: None
        """

        self.customContextMenu.exec_(self.sender().mapToGlobal(point))

    @QtCore.Slot()
    def on_copyAction_triggered(self):
        """
        Slot method for the `copyAction` widget's `triggered` signal.

        :rtype: None
        """

        if clipman is not None:

            clipman.set(self.currentItem().text())

        else:

            log.warning('Unable to copy path to clipboard!')

    @QtCore.Slot()
    def on_exportAction_triggered(self):
        """
        Slot method for the `exportAction` widget's `triggered` signal.

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
