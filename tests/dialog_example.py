from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import QRegExp
import glob, sys, os
from functools import partial
from dvc_x.ui import RemoteFileDialog
from dvc_x.ui import RemoteServerSettingDialog, GenerateKeygenDialog


class MainUI(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)

        pb = QtWidgets.QPushButton(self)
        pb.setText("Configure Connection")
        pb.clicked.connect(lambda: self.openConfigRemote())
        br = QtWidgets.QPushButton(self)
        br.setText("Browse remote")
        br.clicked.connect(lambda: self.browseRemote())
        gp = QtWidgets.QPushButton(self)
        gp.setText("Generate Key")
        gp.clicked.connect(lambda: self.generateKey())

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(pb)
        layout.addWidget(br)
        layout.addWidget(gp)
        widg = QtWidgets.QWidget()
        widg.setLayout(layout)
        self.setCentralWidget(widg)


        self.show()
    def getSelected(self, dialogue):
        if hasattr(dialogue, 'selected'):
            for el in dialogue.selected:
                print ("Return from dialogue", el)
    def getConnectionDetails(self, dialog):
        if dialog.connection_details is not None:
            for k,v in dialog.connection_details.items():
                print (k,v)
        self.connection_details = dialog.connection_details
    def openConfigRemote(self):

        dialog = RemoteServerSettingDialog(self,port=None,
                                    host=None,
                                    username=None,
                                    private_key=None,
                                    settings_filename='remote_config.ini')
        dialog.Ok.clicked.connect(lambda: self.getConnectionDetails(dialog))
        dialog.exec()
    def browseRemote(self):
        # private_key = os.path.abspath("C:\Apps\cygwin64\home\ofn77899\.ssh\id_rsa")
        # port=22
        # host='ui3.scarf.rl.ac.uk'
        # username='scarf595'
        if hasattr(self, 'connection_details'):
            username = self.connection_details['username']
            port = self.connection_details['server_port']
            host = self.connection_details['server_name']
            private_key = self.connection_details['private_key']
            remote_os = self.connection_details['remote_os']

            logfile = os.path.join(os.getcwd(), "RemoteFileDialog.log")
            dialogue = RemoteFileDialog(self,
                                        logfile=logfile,
                                        port=port,
                                        host=host,
                                        username=username,
                                        private_key=private_key,
                                        remote_os=remote_os)
            dialogue.Ok.clicked.connect(lambda: self.getSelected(dialogue))

            dialogue.exec()

    def generateKey(self):
        dialog = GenerateKeygenDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainUI()

    sys.exit(app.exec_())
