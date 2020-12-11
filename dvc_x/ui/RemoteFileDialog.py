import sys
import os
import posixpath
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import QRegExp
import glob
from functools import partial
import dvc_x as drx



class RemoteFileDialog(QtWidgets.QDialog):

    def __init__(self, parent = None, \
        logfile=None, port=None, host=None, username=None, private_key=None):
        QtWidgets.QDialog.__init__(self, parent)

        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        # dialog = QtWidgets.QFileDialog.getOpenFileUrl(self, "select file", dir=url )
        # dialog = QtWidgets.QFileDialog(self, "select file")
        # dialog.selectUrl(url)
        # dialog.show()
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
                                     | QtWidgets.QDialogButtonBox.Cancel)

        bb.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.accepted())
        bb.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(lambda: self.rejected())
        
        # Add vertical layout to dock contents
        vl = QtWidgets.QVBoxLayout(self)
        vl.setContentsMargins(10, 10, 10, 10)

        # create input text for starting directory
        hl, up, line_edit, push_button= self.createLineEditForStartingDirectory()
        # set the focus on the Browse button
        push_button.setDefault(True)
        # create table widget
        tw = self.createTableWidget()

        
        # add Widgets to layout
        vl.addLayout(hl)
        vl.addWidget(push_button)
        vl.addWidget(tw)
        vl.addWidget(bb)

        self.setLayout(vl)

        # save references 
        self.widgets = {'layout': vl, 'buttonBox':bb, 'tableWidget': tw, 
                        'browseButton': push_button, 'lineEdit': line_edit, 
                        'upButton': up, 'horizLayot': hl}
        self.layout = vl
        self.buttonBox = bb
        self.tableWidget = tw
        self.push_button = push_button
        self.line_edit = line_edit

        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.conn = self.setupConnection(logfile=logfile, port=port, \
            host=host, username=username, private_key=private_key)

        self.setWindowTitle("Remote File Explorer on {}@{}:{}".format(username, host, port))
        
    @property
    def Ok(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Ok)

    def setupConnection(self, logfile=None, port=None, host=None, \
            username=None, private_key=None):
        
        a=drx.DVCRem(logfile=logfile, port=port, host=host, username=username, private_key=private_key)

        return a

    def setup_menubar(self):
        pass

    def accepted(self):
        sel = self.tableWidget.selectedItems()
        if len(sel) > 0:
            selected = []
            for it in sel:
                print ("Selected", it.text())
                selected.append((self.widgets['lineEdit'].text(), it.text()))
            self.selected = selected
            self.close()

    def rejected(self):
        self.close()

    def createLineEditForStartingDirectory(self):        
        
        pb = QtWidgets.QPushButton()
        pb.setText("Browse..")
        pb.clicked.connect(lambda: self.globDirectoryAndFillTable())
        
        pb = QtWidgets.QPushButton()
        pb.setText("Browse..")

        
        up = QtWidgets.QPushButton()
        up.setIcon(QtWidgets.QApplication.style().standardPixmap((QtWidgets.QStyle.SP_ArrowUp)))
        up.clicked.connect(lambda: self.goToParentDirectory())
        up.setFixedSize(QtCore.QSize(30,30))
        
        le = QtWidgets.QLineEdit(self)
        le.returnPressed.connect(lambda: self.globDirectoryAndFillTable())
        le.setClearButtonEnabled(True)

        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(up)
        hl.addWidget(le)
        
        return hl, up, le, pb

    def globDirectoryAndFillTable(self):
        # load data into table widget
        # set OverrideCursor to WaitCursor
        QtGui.QGuiApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        directory = posixpath.abspath(self.line_edit.text())
        # print ("trying to list ", directory)
        self.conn.login(passphrase=False)
        data = self.conn.listdir(path=directory)
        # print (data)
        ddata = []
        for el in data[1]:
            ddata.append((data[0], el))
        # print (ddata)
        self.conn.logout()
        self.loadIntoTableWidget(ddata)
        # restore OverrideCursor
        QtGui.QGuiApplication.restoreOverrideCursor()

    def goToParentDirectory(self):
        le = self.widgets['lineEdit']
        if self.isDir(le.text()):
            current_dir = posixpath.dirname(le.text())
        else:
            current_dir = posixpath.abspath(le.text())

        parent_dir = posixpath.abspath(posixpath.join(current_dir, '..'))
        
        le.setText(str(parent_dir))
        self.globDirectoryAndFillTable()

    def isDir(self, path):
        # this should be able to test if the address in the bar is a directory
        # 
        return False

    def createTableWidget(self):
        tableWidget = QtWidgets.QTableWidget()
        tableWidget.itemClicked.connect(self.fillLineEditWithClickedTableItem)
        tableWidget.itemDoubleClicked.connect(self.fillLineEditWithDoubleClickedTableItem)
        tableWidget.setColumnWidth(1,40)
        header = tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        return tableWidget

    def fillLineEditWithClickedTableItem(self, item):
        # self.line_edit.setText(posixpath.join(self.line_edit.text() , item.text()))
        pass

    def fillLineEditWithDoubleClickedTableItem(self, item):
        self.line_edit.setText(posixpath.join(self.line_edit.text() , item.text()))
        #self.push_button.click()
        self.globDirectoryAndFillTable()

    def loadIntoTableWidget(self, data):
        if len(data) <= 0:
            return
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))
        for i, v in enumerate(data):
            for j, w in enumerate(v):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(w)))
        # tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Name'))
        # tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Type'))
        self.tableWidget.setHorizontalHeaderLabels(['Type', 'Name'])
        self.tableWidget.sortItems(1, order=QtCore.Qt.AscendingOrder)

