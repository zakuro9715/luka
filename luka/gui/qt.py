import shutil
import os

from PySide.QtCore import * 
from PySide.QtGui import *

import luka


def removeChildrenRecursive(item, i = 0):
    if i > 50:
        raise Exception()
    while item.count() > 0: 
        child = item.itemAt(0)
        layout, widget = child.layout(), child.widget()
        if layout:
            removeChildrenRecursive(layout, i + 1)
            layout.setParent(None)
        elif widget:
            widget.setParent(None)

class TakeSnapshotWidget(QWidget):
    snapshotTaked = Signal(luka.Snapshot)

    def __init__(self, luka, *args, **kwargs):
        super(TakeSnapshotWidget, self).__init__(*args, **kwargs)
        self.luka = luka

        self.setWindowTitle('Luka - Take snapshot')
        self.setGeometry(50, 50, 250, 150)

        self.layout = QFormLayout(self)

        self.messageEdit = QLineEdit()
        self.layout.addRow('Message', self.messageEdit)

        self.button = QPushButton("take snapshot")
        self.button.clicked.connect(self.buttonClicked)
        self.layout.addRow(self.button)        

        self.setLayout(self.layout)


    def buttonClicked(self):
        s = self.take_snapshot()
        self.snapshotTaked.emit(s)
        self.close()


    def take_snapshot(self):
        message = self.messageEdit.text()
        self.luka.take_snapshot(message)


class SnapshotListWidget(QWidget):  
    def __init__(self, luka, *args, **kwargs):
        super(SnapshotListWidget, self).__init__(*args, **kwargs)
        self.luka = luka
        luka.snapshot_taked.subscribe(lambda sender, s: self.addLine(s))
        luka.snapshot_removed.subscribe(lambda sender, s: self.removeLine(s))
        luka.loaded.subscribe(lambda sender, snapshots: self.resetLines(snapshots))

        self.setWindowTitle('Luka')
        self.initUI()

        if self.luka is not None:
            self.reload()
        else:
            self.showEmptyMessage()
    
    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.snapshotsLayout = QVBoxLayout(self)
        self.layout.addLayout(self.snapshotsLayout)
        self.layout.addWidget(QFrame(self))

        self.reloadButton = QPushButton("Reload", self)
        self.layout.addWidget(self.reloadButton)
        self.reloadButton.clicked.connect(self.reload)

        self.emptyMessageLabel = None
        self.lines = {}
    
    def showEmptyMessage(self):
        if self.emptyMessageLabel is not None:
            return
        self.emptyMessageLabel = QLabel("No snapshots", self)
        self.snapshotsLayout.addWidget(self.emptyMessageLabel)
    
    def hideEmptyMessage(self):
        if self.emptyMessageLabel is None:
            return
        self.emptyMessageLabel.setParent(None)

    def resetLines(self, snapshots):
        removeChildrenRecursive(self.snapshotsLayout)
        self.lines.clear()
        
        if len(snapshots) == 0:
            self.showEmptyMessage()

        for id in sorted(snapshots.keys()):
            self.addLine(snapshots[id])

    def addLine(self, s):
        self.hideEmptyMessage()

        restoreButton = QPushButton("Restore", self)
        restoreButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        restoreButton.clicked.connect(lambda : self.restore(s))
        removeButton = QPushButton("Remove", self)
        restoreButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        removeButton.clicked.connect(lambda : self.remove(s))

        line = QHBoxLayout(self)
        line.addWidget(QLabel(s.message, self))
        line.addWidget(restoreButton)
        line.addWidget(removeButton)
        self.lines[s.id] = line
        self.snapshotsLayout.addLayout(line)

    def removeLine(self, s):
        v = self.lines[s.id]
        removeChildrenRecursive(v)
        v.setParent(None)
        
        if len(self.luka.snapshots) == 0:
            self.showEmptyMessage()
    
    def reload(self):
        self.luka.load()

    def restore(self, s):
        self.luka.restore_snapshot(s)

    def remove(self, s):
        self.luka.remove_snapshot(s)
