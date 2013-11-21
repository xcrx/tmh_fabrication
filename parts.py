import os
from PyQt4 import QtCore, QtGui, QtSql, uic
from new_part import NewPart
from dbConnection import db_err
#TODO: New Part
#TODO: Print list W/ current filter


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
        col = index.column()
        pid_col = mod.columnCount()-1
        pid = int(mod.data(mod.index(row, pid_col)).toString())
        if col == 1:
            old_stock = int(mod.data(mod.index(row, col)).toString())
            new_stock, ok = QtGui.QInputDialog.getInt(None, "New Quantity", "New Quantity", old_stock)
            if ok:
                update = "Update parts_detail set stock=%d where pid=%d" % (new_stock, pid)
                qry = QtSql.QSqlQuery()
                if qry.exec_(update):
                    mod.query().exec_()
                    QtGui.QMessageBox.information(None, "Successful", "Stock updated successfully")
                else:
                    db_err(qry)
        elif col == 5:
            old_cost = mod.data(mod.index(row, col)).toString()
            new_cost, ok = QtGui.QInputDialog.getText(None, "New Price", "New Price", 0, old_cost)
            if ok:
                update = "Update parts_detail set cost=%s where pid=%d" % (new_cost, pid)
                qry = QtSql.QSqlQuery()
                if qry.exec_(update):
                    mod.query().exec_()
                    QtGui.QMessageBox.information(None, "Successful", "Price updated successfully")
                else:
                    db_err(qry)
        else:
            self.goToPart.emit(pid)
