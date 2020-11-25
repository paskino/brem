import sys
import os
import posixpath
from PySide2 import QtCore, QtWidgets
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

        # bb.accepted.connect(self.accepted)
        # print(  bb.button(QtWidgets.QDialogButtonBox.Ok) )
        # Add vertical layout to dock contents
        vl = QtWidgets.QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)

        # create input text for starting directory
        line_edit, push_button = self.createLineEditForStartingDirectory()
        # create table widget
        tw = self.createTableWidget()

        
        # add Widgets to layout
        vl.addWidget(line_edit)
        vl.addWidget(push_button)
        vl.addWidget(tw)
        vl.addWidget(bb)

        # self.setStandardButtons(bb)
        self.setLayout(vl)

        # save references 
        self.layout = vl
        self.buttonBox = bb
        self.tableWidget = tw
        self.push_button = push_button
        self.line_edit = line_edit

        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.conn = self.setupConnection(logfile=logfile, port=port, \
            host=host, username=username, private_key=private_key)

        self.show()
    def setupConnection(self, logfile=None, port=None, host=None, \
            username=None, private_key=None):
        
        a=drx.DVCRem(logfile=logfile, port=port, host=host, username=username, private_key=private_key)

        return a

    def setup_menubar(self):
        pass

    def accepted(self):
        sel = self.tableWidget.selectedItems()
        for it in sel:
            print ("Selected", it.text())
        self.close()

    def rejected(self):
        self.close()

    def createLineEditForStartingDirectory(self):
        le = QtWidgets.QLineEdit(self)
        #rx = QRegExp("[A-Za-z0-9]+")
        #validator = QRegExpValidator(rx, le) #need to check this
        #le.setValidator(validator)
        pb = QtWidgets.QPushButton()
        pb.setText("Browse..")
        pb.clicked.connect(lambda: self.globDirectoryAndFillTable())

        return le, pb

    def globDirectoryAndFillTable(self):
        # load data into table widget
        # data = [('file_{}.tiff'.format(i), '{} kb'.format(i)) for i in range(10)]
        
        # directory = os.path.abspath(self.line_edit.text())

        # data = glob.glob(os.path.join(directory, "*"))
        # ddata = []
        # for el in data:
        #     ddata.append((el, "dir" if os.path.isdir(el) else "file"))
        # self.loadIntoTableWidget(ddata)
        directory = posixpath.abspath(self.line_edit.text())
        print ("trying to list ", directory)
        self.conn.login(passphrase=False)
        data = self.conn.listdir(path=directory)
        print (data)
        ddata = []
        for el in data[1]:
            ddata.append((data[0], el))
        print (ddata)
        self.conn.logout()
        self.loadIntoTableWidget(ddata)


    def createTableWidget(self):
        tableWidget = QtWidgets.QTableWidget()
        tableWidget.itemClicked.connect(self.fillLineEditWithClickedTableItem)
        tableWidget.itemDoubleClicked.connect(self.fillLineEditWithDoubleClickedTableItem)
        tableWidget.setColumnWidth(1,40)
        header = tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        return tableWidget

    def fillLineEditWithClickedTableItem(self, item):
        self.line_edit.setText(posixpath.join(self.line_edit.text() , item.text()))

    def fillLineEditWithDoubleClickedTableItem(self, item):
        self.fillLineEditWithClickedTableItem(item)
        self.push_button.click()

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
        self.tableWidget.setHorizontalHeaderLabels(['Name', 'Type'])
        self.tableWidget.sortItems(1, order=QtCore.Qt.AscendingOrder)

    # if self.interactiveEdit.isChecked() and self.tableDock.isVisible():
    #         position = interactor.GetEventPosition()
    #         print("pick position {}".format(position))
    #         vox = self.vtkWidget.viewer.style.display2imageCoordinate(position, subvoxel=True)
    #         print("pick vox {}".format(vox))
    #         # print("[%d,%d,%d] : %.2g" % vox)
    #         rows = self.tableWidget.rowCount()
    #         cols = self.tableWidget.columnCount()
    #         self.tableWidget.setRowCount(rows + 1)
    #         if cols != 4:
    #             self.tableWidget.setColumnCount(4)
    #         for col in range(3):
    #             self.tableWidget.setItem(rows, col+1,
    #                                      QTableWidgetItem(str(vox[col])))
    #         rows = self.tableWidget.rowCount()
    #         print("rows", rows)
    #         if rows == 1:
    #             el = 1
    #         else:
    #             print("row {0} el {1} ".format(
    #                 rows, self.tableWidget.item(rows-2, 0).text()))
    #             el = int(self.tableWidget.item(rows-2, 0).text())
    #         self.tableWidget.setItem(rows-1, 0, QTableWidgetItem(str(el+1)))
