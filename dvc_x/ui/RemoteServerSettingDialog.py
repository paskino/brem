from PySide2 import QtCore, QtGui, QtWidgets
from dvc_x.ui.UIFormWidget import UIFormFactory
import os

class RemoteServerSettingDialog(QtWidgets.QDialog):
    def __init__(self, parent = None, \
        logfile=None, port=None, host=None, username=None, private_key=None):
        QtWidgets.QDialog.__init__(self, parent)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
                                     | QtWidgets.QDialogButtonBox.Cancel)

        bb.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.accepted())
        bb.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(lambda: self.rejected())
        self.buttonBox = bb

        formWidget = UIFormFactory.getQWidget(parent=self)
        self.formWidget = formWidget
        
        self.createUI()

        # add the button box
        formWidget.uiElements['verticalLayout'].addWidget(bb)
        # set the layout
        self.setLayout(formWidget.uiElements['verticalLayout'])
        self.setWindowTitle("Remote server settings")

        if not port is None:
            self.setServerPort(port)
        if not host is None:
            self.setServerName(host)
        if not username is None:
            self.setUsername(username)
        if not private_key is None:
            self.setPrivateKeyFile(private_key)


        
    def createUI(self):
        '''creates the form view for inputting the remote server data'''
        fw = self.formWidget
        # create the form view

        # add server name
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Server name: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        # finally add to the form widget
        fw.addWidget('server_name', qlabel, qwidget)

        # add server port
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Server port: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        qwidget.setText("22")
        # add validator as this must be a positive integer
        validator = QtGui.QIntValidator()
        validator.setTop(65535)
        qwidget.setValidator(validator)
        # finally add to the form widget
        fw.addWidget('server_port', qlabel, qwidget)
        
        # add user name
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("User name: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        # finally add to the form widget
        fw.addWidget('username', qlabel, qwidget)

        # add private key
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Private key file: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        # finally add to the form widget
        fw.addWidget('private_key', qlabel, qwidget)

        # add private key
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Browse for private key file: ")
        qwidget = QtWidgets.QPushButton(fw.groupBox)
        qwidget.setText("Browse")
        qwidget.clicked.connect(lambda: self.browseForPrivateKeyFile())
        # finally add to the form widget
        fw.addWidget('button_private_key', qlabel, qwidget)

    @property
    def Ok(self):
        return self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
    
    # set values programmatically
    def setServerName(self, value):
        self.formWidget.widgets['server_name_field'].setText(value)
    def setServerPort(self, value):
        if value >=0 and value < 65535:
            self.formWidget.widgets['server_port_field'].setText(str(value))
    def setUsername(self, value):
        self.formWidget.widgets['username_field'].setText(value)
    def setPrivateKeyFile(self, value):
        if os.path.exists(os.path.abspath(value)):
            self.formWidget.widgets['private_key_field'].setText(value)
    #

    def accepted(self):
        server_name = self.formWidget.widgets['server_name_field'].text()
        server_port = self.formWidget.widgets['server_port_field'].text()
        username    = self.formWidget.widgets['username_field'].text()
        private_key = os.path.join( self.formWidget.widgets['private_key_field'].text() )

        error = 0 
        error_msg = ''
        if server_name == '':
            error_msg += "provide server name\n"
            error += 1
        if server_port == '':
            error_msg += "provide server port\n"
            error += 10
        if username == '':
            error_msg += "provide user name\n"
            error += 100
        if not os.path.exists(private_key):
            error_msg += "provide private key file"
            error += 1000

        if error > 0:
            # print ("Error", error)
            # print (error_msg)
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("Error {}".format(error))
            msg.setDetailedText(error_msg)
            msg.exec()
        else:
            print ("connecting {}@{}:{} with private key {}".format(username, server_name, server_port, private_key))
            self.connection_details = {'username': username, 'server_name': server_name, 
                                       'server_port': server_port, 'private_key': private_key}
            self.close()

    def rejected(self):
        self.close()

    def browseForPrivateKeyFile(self):
        dialogue = QtWidgets.QFileDialog(self)
        mask = dialogue.getOpenFileName(self,"Select the private key file")[0]
        if mask is not None:
            self.formWidget.widgets['private_key_field'].setText(os.path.abspath(mask))
