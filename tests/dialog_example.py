from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import QRegExp
import glob, sys, os
from functools import partial
from dvc_x.ui import RemoteFileDialog
from dvc_x.ui import RemoteServerSettingDialog


class MainUI(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        url = None
        private_key = os.path.abspath("C:\Apps\cygwin64\home\ofn77899\.ssh\id_rsa")
        port=22
        host='ui3.scarf.rl.ac.uk'
        username='scarf595'
        logfile = os.path.join(os.getcwd(), "RemoteFileDialog.log")
        logfile = os.path.abspath("C:/Users/ofn77899/Documents/Projects/CCPi/GitHub/PythonWorkRemote/dvc_x/RemoteFileDialogue.log")
        dialogue = RemoteFileDialog(self,
                                    logfile=logfile, 
                                    port=port, 
                                    host=host, 
                                    username=username,
                                    private_key=private_key)
        dialogue.Ok.clicked.connect(lambda: self.getSelected(dialogue))
        
        dialog = RemoteServerSettingDialog(self,port=port, 
                                    host=host, 
                                    username=username,
                                    private_key=private_key)
        dialog.Ok.clicked.connect(lambda: self.getConnectionDetails(dialog))
        dialog.exec()
        # dialogue.exec()


        self.show()
    def getSelected(self, dialogue):
        if hasattr(dialogue, 'selected'):
            for el in dialogue.selected:
                print ("Return from dialogue", el)
    def getConnectionDetails(self, dialog):
        for k,v in dialog.connection_details.items():
            print (k,v)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainUI()
    
    sys.exit(app.exec_())