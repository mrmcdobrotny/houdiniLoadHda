import sys, os, glob, platform, json, hou

from PySide2.QtWidgets import *
from PySide2 import QtCore
from PySide2 import QtGui

from uiHoudiniLoadhda import Ui_Form


class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.readPreset()
        self.initList()
        self.updatePresetList()
        self.loadPreset()
        
        self.lineEditFilter.textChanged.connect(self.filterList)
        self.pushCheck.clicked.connect(self.checkSelected)
        self.pushUncheck.clicked.connect(self.uncheckSelected)
        self.pushLoadHda.clicked.connect(self.installAssets)
        self.pushSavePreset.clicked.connect(self.savePreset)
        self.pushLoadPreset.clicked.connect(self.loadPreset)
        self.comboBox.currentTextChanged.connect(self.loadPreset)

    def closeEvent(self, event):
        self.setParent(None)
        #self.close()
        

    def initList(self):
        self.model = QtGui.QStandardItemModel(self)
        root = "/media/white/tools/otls"
        self.hda_paths = glob.glob(os.path.join(root, "*.hda"))
        self.hda_names = [os.path.split(filepath)[1] for filepath in self.hda_paths]
        self.loadedHda = []
        [self.loadedHda.append(os.path.split(path)[1]) for path in hou.hda.loadedFiles()]
        #print(self.loadedHda)

        for row, file in enumerate(self.hda_names):
            item = QtGui.QStandardItem("{}".format(file))
            item.setCheckable(True)
            inHdaFolder = file in self.loadedHda
            #print(self.hda_paths[row])
            if inHdaFolder:
                item.setCheckState(QtCore.Qt.CheckState.Checked)
            #definitions = hou.hda.definitionsInFile(self.hda_paths[row])
            comment_text = "comment"
            #for definition in definitions:
            #    comment_text += definition.nodeTypeName()
            
            comment = QtGui.QStandardItem("{}".format(comment_text))
            

            self.model.invisibleRootItem().appendRow([item, comment])


        #self.model.setHorizontalHeaderLabels(self.hda_labels)
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.listView.setModel(self.proxy)
        
        #self.listView.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)


    def filterList(self):
        text = self.lineEditFilter.text()
        search = QtCore.QRegExp(    text,
                                    QtCore.Qt.CaseInsensitive,
                                    QtCore.QRegExp.RegExp
                                    )

        self.proxy.setFilterRegExp(search)

    def installAssets(self):
        selectionModel = self.listView.selectionModel()
        selected = selectionModel.selectedIndexes()

        for row, file in enumerate(self.hda_paths):
            
            #index = self.proxy.index(row,column)
            #srcIndex = self.proxy.mapToSource(index)
            index = self.model.index(row,0)
            proxyIndex = self.proxy.mapFromSource(index)
            
            item = self.model.itemFromIndex(index)
            checkState = item.checkState()
            if checkState == QtCore.Qt.CheckState.Checked:
                hdaInstalled = self.hda_names[row] in self.loadedHda
                if not hdaInstalled:
                    print("Installing HDA {}".format(self.hda_names[row]))
                    hou.hda.installFile(file)


    def checkSelected(self):
        selectionModel = self.listView.selectionModel()
        selected = selectionModel.selectedIndexes()
        for index in selected:
            srcIndex = self.proxy.mapToSource(index)
            self.model.itemFromIndex(srcIndex).setCheckState(QtCore.Qt.CheckState.Checked)

    def uncheckSelected(self):
        selectionModel = self.listView.selectionModel()
        selected = selectionModel.selectedIndexes()
        for index in selected:
            srcIndex = self.proxy.mapToSource(index)
            self.model.itemFromIndex(srcIndex).setCheckState(QtCore.Qt.CheckState.Unchecked)
    def readPreset(self):
        self.preset_path = "/media/white/tools/scripts/houdini/houdiniLoadHda/.userpresets"
        try:
            with open(self.preset_path, 'r') as f:
                try:
                    self.preset = json.load(f)
                except ValueError:
                    self.preset = {}
        except IOError:
            self.preset = {}

    def updatePresetList(self):
        keys = self.preset.keys()
        self.comboBox.clear()
        for key in keys:
            self.comboBox.addItem(key)

    def loadPreset(self):
        for row, file in enumerate(self.hda_paths):
            index = self.model.index(row,0)
            proxyIndex = self.proxy.mapFromSource(index)
            item = self.model.itemFromIndex(index)

            listOfCheckedItems = self.preset[self.comboBox.currentText()]
            if self.hda_names[row] in listOfCheckedItems:
                item.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def savePreset(self):
        #preset_path = os.path.join(*[os.environ["HOME"], "houdini18.5", ".houdiniLoadHdaPresets"] )
        
        listOfCheckedItems = []
        for row, file in enumerate(self.hda_paths):
            index = self.model.index(row,0)
            proxyIndex = self.proxy.mapFromSource(index)
            item = self.model.itemFromIndex(index)
            checkState = item.checkState()
            if checkState == QtCore.Qt.CheckState.Checked:
                listOfCheckedItems.append(self.hda_names[row])
        

        with open(self.preset_path, 'w') as f:

            self.preset[self.comboBox.currentText()] = listOfCheckedItems
            jsn = json.dumps(self.preset, indent=4)
            f.write(jsn)


def main():
    if __name__ == 'houdiniLoadHdaMain':
        #print(__name__)
        #app = QtWidgets.QApplication()
        mainWin = MainWindow()
        mainWin.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        #mainWin.setParent(None)
        mainWin.show()