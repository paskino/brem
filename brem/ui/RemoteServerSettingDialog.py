from PySide2 import QtCore, QtGui, QtWidgets
from eqt.ui.UIFormWidget import UIFormFactory
import os
import configparser
import brem
from eqt.threading.QtThreading import Worker, WorkerSignals, ErrorObserver




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
        self._connection_details = None

        self.loadConnectionSettingsFromFile()


    @property
    def settings_filename(self):
        return self._settings_filename

    @settings_filename.setter
    def settings_filename(self, value):
        if value is None:
            self._settings_filename = os.path.join(os.path.expanduser('~'), 'remote_config.ini')
            return
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
        fw.addWidget(qwidget, qlabel, 'server_name' )

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
        fw.addWidget(qwidget, qlabel, 'server_port')
        
        # add user name
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("User name: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        # finally add to the form widget
        fw.addWidget(qwidget, qlabel, 'username')

        # add user name
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Remote OS: ")
        qwidget = QtWidgets.QComboBox(fw.groupBox)
        qwidget.addItem("POSIX")
        qwidget.addItem("Windows")
        qwidget.setCurrentIndex(0)
        qwidget.setEnabled(True)
        # finally add to the form widget
        fw.addWidget(qwidget, qlabel, 'remote_os')

        # add private key
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Private key file: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        # finally add to the form widget
        fw.addWidget(qwidget, qlabel, 'private_key')

        # add private key
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Browse for private key file: ")
        qwidget = QtWidgets.QPushButton(fw.groupBox)
        qwidget.setText("Browse")
        qwidget.clicked.connect(lambda: self.browseForPrivateKeyFile())
        # finally add to the form widget
        fw.addWidget(qwidget, qlabel, 'button_private_key')
    
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
    def setRemoteOS(self, value):
        idx = 0 if value == 'POSIX' else 1
        self.formWidget.widgets['remote_os_field'].setCurrentIndex(idx)
    #

    def accepted(self):
        server_name = self.formWidget.widgets['server_name_field'].text()
        server_port = self.formWidget.widgets['server_port_field'].text()
        username    = self.formWidget.widgets['username_field'].text()
        private_key = os.path.join( self.formWidget.widgets['private_key_field'].text() )
        remote_os = self.formWidget.widgets['remote_os_field'].currentText()

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

        if error >=  1000:
            # should pop up a message Dialog saying that a key will be generated
            # and will be asked for a password
            keygen_dialog = self.generateKeyFileDialog(parent=self)
            keygen_dialog.show()

        elif error > 0:
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
                                       'server_port': server_port, 
                                       'private_key': private_key,
                                       'remote_os' : remote_os }
            self.storeConnectionDetails(self.connection_details)
            
            self.close()
    @property
    def connection_details(self):
        return self._connection_details
    @connection_details.setter
    def connection_details(self, value):
        if isinstance(value, dict):
            self._connection_details = value
    def updateSettingsWithNewlyGeneratedKeyFile(self):
        print ("updateSettingsWithNewlyGeneratedKeyFile")

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
            self.setRemoteOS(c['remote_os'])
        
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
        
    def generateKeyFileDialog(self, parent=None):
        '''return a Dialog to generate and save an SSH public/private key'''
        server_name = self.formWidget.widgets['server_name_field'].text()
        server_port = self.formWidget.widgets['server_port_field'].text()
        username    = self.formWidget.widgets['username_field'].text()
        
        keygen_dialog = GenerateKeygenDialog(parent=self, 
                            host=server_name, port=server_port, username=username)
        # keygen_dialog.Ok.clicked.connect(lambda: self.updateSettingsWithNewlyGeneratedKeyFile())
        keygen_dialog.finished.connect(lambda x: self.retrieveNewlyGeneratedKeyFile(keygen_dialog,x))
        return keygen_dialog

    def retrieveNewlyGeneratedKeyFile(self, keygen_dialog,value):
        '''fills the path to the key file from the GenerateKeyDialog'''
        print ("retrieveNewlyGeneratedKeyFile", value)
        self.setPrivateKeyFile(keygen_dialog.key_file)


class GenerateKeygenDialog(QtWidgets.QDialog):
    '''A dialog to generate a SSH key pair
    
    Will ask for the password. It will require the host, port and username to be passed.

    This dialog is launched by the RemoteServerSettingDialog if the private key field
    is left blank. In such a case a new key pair will be:

    1) created and saved locally
    2) uploaded to the remote and saved into the .ssh/authorized_keys file.

    2 will happen in a QThread.
    '''
    def __init__(self, parent=None, host=None, port=22, username=None):
        QtWidgets.QDialog.__init__(self, parent)

        # save a reference of the host,port and username
        self.host = host
        self.port = port
        self.username = username

        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
                                     | QtWidgets.QDialogButtonBox.Cancel)

        bb.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.accepted())
        bb.button(QtWidgets.QDialogButtonBox.Ok).setText("Generate Key and save")
        bb.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(lambda: self.rejected())
        self.buttonBox = bb

        fw = UIFormFactory.getQWidget(parent=self)
        self.formWidget = fw

        # create the form view

        # add server name
        qlabel = QtWidgets.QLabel(fw.groupBox)
        qlabel.setText("Server password: ")
        qwidget = QtWidgets.QLineEdit(fw.groupBox)
        qwidget.setClearButtonEnabled(True)
        qwidget.setEchoMode(QtWidgets.QLineEdit.Password)
        # finally add to the form widget
        fw.addWidget(qwidget, qlabel, 'server_password')

        # insert a QLabel at the top to describe what's happening
        self.infolabel = QtWidgets.QLabel()
        self.setInfo('A new SSH key will be generated for \nuser {} on {}:{}\nPlease provide your password'.format(username, host, port))
        self.formWidget.uiElements['verticalLayout'].insertWidget(0,self.infolabel)

        
        # add the button box
        fw.uiElements['verticalLayout'].addWidget(bb)
        # set the layout
        self.setLayout(fw.uiElements['verticalLayout'])
        self.setWindowTitle("Remote server settings")
        self._key_file = None
        self.threadpool = QtCore.QThreadPool()
    @property
    def Ok(self):
        '''returns a reference to the OK button in the dialog button box'''
        return self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)

    @property
    def key_file(self):
        return self._key_file
    @key_file.setter
    def key_file(self, value):
        self._key_file = os.path.abspath(value)
    
    def accepted(self):
        '''authorize the key on the remote server'''
        self.setFilenameForPrivateKeyFile()
        if self.key_file is not None:
            self.keygen_authorise = Worker(self.authorize_key_worker, self.host, 
                                            self.username, self.port)
            self.keygen_authorise.signals.message.connect(self.setInfo)
            self.keygen_authorise.signals.error.connect(self.handleError)
            self.keygen_authorise.signals.finished.connect(self.authorised)
            self.threadpool.start(self.keygen_authorise)
            
    def handleError(self, error):
        print (error)
        errormsg = error[1]
        if errormsg is not None:
            # send message to user
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("Error {}".format(str(errormsg)))
            msg.exec()
            
    def authorised(self):
        self.done(1)
        self.close()

    def rejected(self):
        self.done(-1)
        self.close()

    def setFilenameForPrivateKeyFile(self):
        dialogue = QtWidgets.QFileDialog(self)
        dialogue.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        mask = dialogue.getSaveFileName(self,"Save the generated private key file")[0]
        if mask is not None:
            # self.formWidget.widgets['private_key_field'].setText(os.path.abspath(mask))
            self.key_file = mask

    def setInfo(self, text):
        '''Writes in the top QLabel information for the user'''
        self.infolabel.setText(text)

    def authorize_key_worker(self, host, username, port, **kwargs):

        message_callback = kwargs.get('message_callback')
        a = brem.BasicRemoteExecutionManager(logfile='generatekey.log',
                                             port=port,
                                             host=host,
                                             username=username,
                                             private_key=None)

        a.login_pw(self.formWidget.widgets['server_password_field'].text())
        message_callback.emit("Generating Key...")
        a.generate_keys(filename=self.key_file)
        message_callback.emit("Logging onto remote host and authorising key")
        a.authorize_key(filename=self.key_file)
    