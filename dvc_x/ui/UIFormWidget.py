from PySide2 import QtCore, QtWidgets, QtGui
# from PyQt5.QtWidgets import QProgressDialog, QDialog, QLabel, QComboBox, QDialogButtonBox, QFormLayout, QWidget, QVBoxLayout, \
#     QGroupBox, QLineEdit, QMessageBox, QPushButton


        

class UIFormWidget(object):
    '''
             QWidget or QDockWidget
    +----------------------------------------------------------+
    |        QVBoxLayout                                       |
    |   +---------------------------------------------------+  |
    |   |    QWidget                                        |  |
    |   |                                                   |  |
    |   |    +------------------------------------------+   |  |
    |   |    |   QVBoxLayout                            |   |  |
    |   |    |                                          |   |  |
    |   |    |                                          |   |  |
    |   |    +------------------------------------------+   |  |
    |   |                                                   |  |
    |   +---------------------------------------------------+  |
    |                                                          |
    +----------------------------------------------------------+
    '''
    def createForm(self):
        # Add vertical layout to dock contents
        dockContentsVerticalLayout = QtWidgets.QVBoxLayout(self)
        dockContentsVerticalLayout.setContentsMargins(10, 10, 10, 10)

        # Create widget for dock contents
        internalDockWidget = QtWidgets.QWidget(self)

        # Add vertical layout to dock widget
        #internalWidgetVerticalLayout = QtWidgets.QVBoxLayout(internalDockWidget)
        #internalWidgetVerticalLayout.setContentsMargins(0, 0, 0, 0)

        dockContentsVerticalLayout.addWidget(internalDockWidget)
        
        # Add group box
        paramsGroupBox = QtWidgets.QGroupBox(internalDockWidget)


        # Add form layout to group box
        groupBoxFormLayout = QtWidgets.QFormLayout(paramsGroupBox)

        # Add elements to layout
        dockContentsVerticalLayout.addWidget(paramsGroupBox)
        #dockWidget.setWidget(dockWidgetContents)

        self.num_widgets = 0
        self.uiElements = {
                'verticalLayout':dockContentsVerticalLayout, 
                'internalWidget': internalDockWidget,
                #'internalVerticalLayout': internalWidgetVerticalLayout, 
                'groupBox' : paramsGroupBox,
                'groupBoxFormLayout': groupBoxFormLayout}
        self.widgets = {}

    @property
    def groupBox(self):
        return self.uiElements['groupBox']
                
    def addWidget(self, name, qlabel, qwidget):

        formLayout = self.uiElements['groupBoxFormLayout']
                
        #Create the widgets:

        widgetno = self.num_widgets

        # add the label
        label = '{}_label'.format(name)
        formLayout.setWidget(widgetno, QtWidgets.QFormLayout.LabelRole, qlabel)

        # add the field
        field = '{}_field'.format(name)
        formLayout.setWidget(widgetno, QtWidgets.QFormLayout.FieldRole, qwidget)

        # save a reference to the widgets in the dictionary
        self.widgets[label] = qlabel
        self.widgets[field] = qwidget
        self.num_widgets += 1



class FormWidget(QtWidgets.QWidget, UIFormWidget):
    def __init__(self, parent=None):
    # dockWidgetContents = QtWidgets.QWidget()
        
        QtWidgets.QWidget.__init__(self, parent)
        self.createForm()

class FormDockWidget(QtWidgets.QDockWidget, UIFormWidget):
    def __init__(self, parent=None, title=None):
    # dockWidgetContents = QtWidgets.QWidget()
        
        QtWidgets.QDockWidget.__init__(self, parent)
        self.createForm()
        if title is not None:
            self.setObjectName(title)

class UIFormFactory(QtWidgets.QWidget):
# def generateUIFormView(QtWidgets.QWidget):
    '''creates a widget with a form layout group to add things to

    basically you can add widget to the returned groupBoxFormLayout and paramsGroupBox
    The returned dockWidget must be added with
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
    '''
    @staticmethod
    def getQDockWidget(parent=None):
        return FormDockWidget(parent)
    @staticmethod
    def getQWidget(parent=None):
        return FormWidget(parent)