import shutil
import os
import base64

from PySide.QtCore import * 
from PySide.QtGui import *
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from maya import cmds

from luka import Luka
from luka.gui.qt import TakeSnapshotWidget, SnapshotListWidget

__all__ = ['LukaTakeSnapshotUI', 'LukaUI']


def currentScenePath():
    return cmds.file(q=True, sceneName=True).replace('/', '\\')


class LukaTakeSnapshotUI(MayaQWidgetBaseMixin, TakeSnapshotWidget):  
    def __init__(self, luka=None, *args, **kwargs):
        if luka is None:
            scene = currentScenePath()
            luka = Luka(scene, load=True) if len(scene) > 0 else None
        super(LukaTakeSnapshotUI, self).__init__(luka=luka, *args, **kwargs)

    def take_snapshot(self):
        cmds.file(save=True)
        super(LukaTakeSnapshotUI, self).take_snapshot()



class LukaUI(MayaQWidgetBaseMixin, SnapshotListWidget):  
    def __init__(self, *args, **kwargs):
        scene = currentScenePath()
        self.luka = Luka(scene, load=True) if len(scene) > 0 else None
        super(LukaUI, self).__init__(luka=self.luka, *args, **kwargs)

    
    def initUI(self):
        super(LukaUI, self).initUI()

        self.newSnapshotButton = QPushButton("New Snapshot", self)
        self.newSnapshotButton.clicked.connect(self.showTakeSnapshotUI)

        self.layout.addWidget(self.newSnapshotButton)


    def showTakeSnapshotUI(self):
        ui = LukaTakeSnapshotUI(luka=self.luka)
        ui.show()

    def restore(self, s):
        super(LukaUI, self).restore(s)
      
        v = cmds.confirmDialog(
            title='Restore snapshot',
            message='All changes including SAVED will be lost. Are you sure?',
            button=['OK','Cancel'], defaultButton='OK',
            cancelButton='Cancel', dismissString='Cancel')
        if v != 'OK':
            return
        
        cmds.file(cmds.file(q=True, sceneName=True), open=True, force=True)

    def remove(self, s):
        v = cmds.confirmDialog(
            title='Remove snapshot',
            message='Are you sure?',
            button=['OK','Cancel'], defaultButton='OK',
            cancelButton='Cancel', dismissString='Cancel')
        if v != 'OK':
            return
        
        super(LukaUI, self).remove(s)
       