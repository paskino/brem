from PySide2 import QtCore, QtGui, QtWidgets
from dvc_x.ui.UIFormWidget import UIFormFactory
import os
import configparser


class RemoteServerSettingDialog(QtWidgets.QDialog):
    def __init__(self, parent = None, \
        settings_filename=None, port=None, host=None, username=None, private_key=None):
        QtWidgets.QDialog.__init__(self, parent)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
                                     | QtWidgets.QDialogButtonBox.Cancel)

        bb.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.accepted())
        bb.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(lambda: self.rejected())
        self.buttonBox = bb

        formWidget = UIFormFactory.getQWidget(parent=self)
        self.formWidget = formWidget

        # add ComboBox for pre selection, also with a label
        cwidget, combo = self.createPresetComboBox()
        self.combo = combo

        formWidget.uiElements['verticalLayout'].insertWidget(0,cwidget)

        
        self.createFormWidget()

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
        
        self.settings_filename = settings_filename

        self.loadConnectionSettingsFromFile()


    @property
    def settings_filename(self):
        return self._settings_filename

    @settings_filename.setter
    def settings_filename(self, value):
        dpath = os.path.abspath(value)
        if os.path.isdir(dpath):
            self._settings_filename = os.path.join(dpath, 'remote_config.ini')
        elif os.path.isfile(dpath):
            self._settings_filename = dpath
        elif os.path.exists(dpath):
            raise ValueError('{} exists and is not a file or a directory'.format(dpath))
        else:
            self._settings_filename = dpath

    def createFormWidget(self):
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
    
    def createPresetComboBox(self):
        combo = QtWidgets.QComboBox()
        combo.activated.connect(lambda x: self.populateConnectionForm(x))
        
        cwidget = QtWidgets.QWidget()
        clayout = QtWidgets.QFormLayout()
        # add the label
        qlabel = QtWidgets.QLabel()
        qlabel.setText("Presets: ")
        clayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, qlabel)

        # add the field
        clayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, combo)
        # add delete preset button

        pb = QtWidgets.QPushButton()
        pb.setText("Delete Preset")
        pb.clicked.connect(lambda: self.deleteConnectionSetting())
        clayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, pb)

        cwidget.setLayout(clayout)

        

        return cwidget, combo

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
            self.storeConnectionDetails(self.connection_details)
            
            self.close()

    def rejected(self):
        self.close()

    def browseForPrivateKeyFile(self):
        dialogue = QtWidgets.QFileDialog(self)
        mask = dialogue.getOpenFileName(self,"Select the private key file")[0]
        if mask is not None:
            self.formWidget.widgets['private_key_field'].setText(os.path.abspath(mask))
    
    def populateConnectionForm(self, index):
        value = self.combo.currentText()
        print ("Selected text ", index, value)
        config = configparser.ConfigParser()
        config.read(self.settings_filename)
        if value in config.sections():
            c = config[value]
            self.setServerName(c['server_name'])
            self.setServerPort(int(c['server_port']))
            self.setUsername(c['username'])
            self.setPrivateKeyFile(c['private_key'])
        
    def storeConnectionDetails(self, details):
        config = configparser.ConfigParser()
        if os.path.exists(self.settings_filename):
            config.read(self.settings_filename)
        shortname = '{}@{}'.format(details['username'],details['server_name'])
        config[shortname] = details
        self.combo.addItem(shortname)
        with open(self.settings_filename,'w') as f:
            config.write(f)

    def loadConnectionSettingsFromFile(self, filename=None):
        config = configparser.ConfigParser()
        config.read(self.settings_filename)
        for value in config.sections():
            c = config[value]
            shortname = '{}@{}'.format(c['username'],c['server_name'])
            self.combo.addItem(shortname)
        self.combo.setCurrentIndex(-1)
    
    def deleteConnectionSetting(self):
        index = self.combo.currentIndex()
        if index == -1:
            return
        value = self.combo.currentText()
        print ("Selected text ", index, value)
        config = configparser.ConfigParser()
        config.read(self.settings_filename)

        config.pop(value)
        with open(self.settings_filename,'w') as f:
            config.write(f)

        # remove from combo
        self.combo.removeItem(index)
        
