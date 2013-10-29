__author__ = 'rhanson'
import os
from PyQt4 import QtCore, QtGui, QtSql, uic
from new_part import NewPart


class Parts(QtGui.QWidget):
    goToPart = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        def connections():
            self.filter.textEdited.connect(self.filter_)
            self.table_parts.doubleClicked.connect(self.go_to_part)
            self.button_new_part.clicked.connect(self.new_part)

        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/parts.ui', self)
        connections()
        self.load_parts()

    def load_parts(self):
        old_mod = self.table_parts.model()
        mod = QtSql.QSqlQueryModel()
        if old_mod is not None:
            pos = self.table_parts.currentIndex()
        else:
            pos = mod.index(0, 0)
        mod.setQuery('select * from view_parts')
        self.table_parts.setModel(mod)
        self.table_parts.setCurrentIndex(pos)
        self.table_parts.resizeColumnsToContents()

    def filter_(self, text):
        mod = self.table_parts.model()
        rows = mod.rowCount()
        cols = mod.columnCount()
        for row in range(rows):
            hide = True
            for col in range(cols):
                if text.toLower() in mod.data(mod.index(row, col)).toString().toLower():
                    hide = False
            self.table_parts.setRowHidden(row, hide)

    def new_part(self):
        new_part = NewPart()
        part_id = None
        while not part_id:
            part_id = new_part.get_data()
        if part_id != "Cancel":
            self.load_parts()
            self.goToPart.emit(int(part_id))

    def go_to_part(self, index):
        mod = index.model()
        row = index.row()
        col = mod.columnCount()-1
        pid = int(mod.data(mod.index(row, col)).toString())
        self.goToPart.emit(pid)
