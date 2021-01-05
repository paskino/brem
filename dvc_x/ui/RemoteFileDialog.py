import sys
import os
import posixpath, ntpath
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import QRegExp
import glob
from functools import partial
import dvc_x as drx
import stat
from dvc_x.QtThreading import Worker

dpath = os.path

class RemoteFileDialog(QtWidgets.QDialog):

    def __init__(self, parent = None, \
        logfile=None, port=None, host=None, username=None, private_key=None,
        remote_os=None):
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
            host=host, username=username, private_key=private_key,
            remote_os=remote_os)

        self.setWindowTitle("Remote File Explorer on {}@{}:{}".format(username, host, port))
        self.threadpool = QtCore.QThreadPool()
        
    @property
    def Ok(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Ok)

    def setupConnection(self, logfile=None, port=None, host=None, \
            username=None, private_key=None, remote_os=None):
        
        a=drx.DVCRem(logfile=logfile, port=port, host=host, username=username, private_key=private_key)
        global dpath 
        dpath = posixpath 
        if remote_os == 'Windows':
            dpath = ntpath
        print (remote_os, dpath)
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
        directory = dpath.abspath(self.line_edit.text())
        # print ("trying to list ", directory)
        self.conn.login(passphrase=False)
        err = None
        try:
            data = self.conn.listdir(path=directory)
        except FileNotFoundError as error:
            # restore OverrideCursor
            QtGui.QGuiApplication.restoreOverrideCursor()
            err = error
        except PermissionError as error:
            # restore OverrideCursor
            QtGui.QGuiApplication.restoreOverrideCursor()
            err = error
        if err is not None:
            # restore previously selected path
            le = self.widgets['lineEdit']
            parent_dir = self.getCurrentParentRemoteDirectory()
            le.setText(str(parent_dir))
            # send message to user
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("Error {}".format(str(err)))
            msg.exec()
            return
        # print (data)
        ddata = []
        for el in data[1]:
            ddata.append((data[0], el))
        # print (ddata)
        self.conn.logout()
        self.loadIntoTableWidget(ddata)
        # restore OverrideCursor
        QtGui.QGuiApplication.restoreOverrideCursor()

    def getCurrentRemoteDirectory(self):
        le = self.widgets['lineEdit']
        if self.isDir(le.text()):
            current_dir = dpath.abspath(le.text())
        else:
            current_dir = dpath.dirname(le.text())
        return current_dir
    def getCurrentParentRemoteDirectory(self):
        current_dir = self.getCurrentRemoteDirectory()
        return dpath.abspath(dpath.join(current_dir, '..'))

    def goToParentDirectory(self):
        le = self.widgets['lineEdit']
        current_dir = self.getCurrentRemoteDirectory()
        parent_dir  = self.getCurrentParentRemoteDirectory()
        print ("current_dir, parent_dir", current_dir, parent_dir )
        le.setText(str(parent_dir))
        self.globDirectoryAndFillTable()



    def createTableWidget(self):
        tableWidget = QtWidgets.QTableWidget()
        tableWidget.itemClicked.connect(self.fillLineEditWithClickedTableItem)
        tableWidget.itemDoubleClicked.connect(self.fillLineEditWithDoubleClickedTableItem)
        tableWidget.setColumnWidth(1,40)
        header = tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        return tableWidget

    def fillLineEditWithClickedTableItem(self, item):
        pass

    def fillLineEditWithDoubleClickedTableItem(self, item):
        row = item.row()
        fsitem = self.tableWidget.item(row, 1)
        # test if the join dir is still a directory or is a file
        new_path = dpath.join(self.line_edit.text() , fsitem.text())
        if self.isFile(new_path):
            # it should select and close
            self.Ok.click()
            return
        self.line_edit.setText(new_path)
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
                
        self.tableWidget.setHorizontalHeaderLabels(['Type', 'Name'])
        
        self.tableWidget.sortItems(1, order=QtCore.Qt.AscendingOrder)
        self.tableWidget.resizeColumnsToContents()
        self.updateTypeColumn()

    def updateTypeColumn(self):
        for i in range(self.tableWidget.rowCount()):
            w = self.tableWidget.item(i,1).text()
    
            path = dpath.join(self.line_edit.text(), w)
            port = self.conn.port
            host = self.conn.host
            username = self.conn.username
            private_key = self.conn.private_key
            remote_os = self.conn.remote_os
            worker = Worker(self.asyncStatRemotePath, path, i, self.tableWidget, 
                                host, port, username, private_key, remote_os)
            self.threadpool.start(worker)
            
    def isFile(self, path):
        error = None
        try:
            self.conn.login(passphrase=False)
            rstat = self.conn.stat(path)
            self.conn.logout()
            return stat.S_IFMT(rstat.st_mode) == stat.S_IFREG
        except TimeoutError as err:
            error = err
        except Exception as err:
            error = err
        if error is not None:
            # send message to user
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("Error {}".format(str(error)))
            msg.exec()
            return
    def isDir(self, path):
        error = None
        try:
            self.conn.login(passphrase=False)
            rstat = self.conn.stat(path)
            self.conn.logout()
            return stat.S_IFMT(rstat.st_mode) == stat.S_IFDIR
        except TimeoutError as err:
            error = err
        except Exception as err:
            error = err
        if error is not None:
            # send message to user
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("Error {}".format(str(err)))
            msg.exec()
            return
    
    def asyncStatRemotePath(self, path, row, table, host, port, username, private_key, remote_os,
                           progress_callback, message_callback):
        '''asynchronously stat remote files for their type and adds info to the tablewidget'''
        # TODO logfile should be created and deleted
        logfile = 'logfile.log'
        conn = drx.DVCRem(logfile=logfile, 
                          port=port, host=host, username=username, 
                          private_key=private_key)
        error = None
        try:
            conn.login(passphrase=False)
            rstat = conn.stat(path)
            conn.logout()
        except TimeoutError as err:
            error = err
        except Exception as err:
            error = err
        if error is not None:
            # send message to user
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(error)))
        else:
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(rstat)))


