import os
from PyQt4 import QtCore, QtGui, QtSql, uic
from dbConnection import db_err
#TODO: Set up connections
#TODO: Save edits


class Part(QtGui.QWidget):
    goToOrder = QtCore.pyqtSignal([str])
    goToPart = QtCore.pyqtSignal([str])

    def __init__(self, pid, parent=None):
        self.pid = pid

        def connections():
            pass

        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/part.ui', self)

        if not self.load_part:
            self.close()
        if not self.load_drawing():
            pass
        if not self.load_orders():
            QtGui.QMessageBox.information(None, "Orders Unavailable.", "Could not load orders related to %s" % self.pid)
        if self.has_bom.isChecked():
            if not self.load_bom():
                QtGui.QMessageBox.information(None, "BOM Unavailable.", "Could not load bom related to %s" % self.pid)

        connections()
        title = "%s (%s)" % (self.part_number.text(), self.pid)
        self.setWindowTitle(title)

    @property
    def load_part(self):
        qry = QtSql.QSqlQuery()
        data = "Select * from view_parts where `Part ID` = '%s'" % self.pid
        if qry.exec_(data):
            if qry.first():
                self.part_number.setText(qry.value(0).toString())
                self.stock.setText(qry.value(1).toString())
                self.description.setText(qry.value(2).toString())
                self.material.setText(qry.value(3).toString())
                self.cut_time.setTime(qry.value(4).toTime())
                self.cost.setText(qry.value(5).toString())
                if qry.value(6).toString() == '0':
                    self.has_bom.setChecked(False)
                else:
                    self.has_bom.setChecked(True)
                return True
            else:
                QtGui.QMessageBox.critical(None, "Not Found", "A part matching %s could not be found" % self.pid)
                return False
        else:
            db_err(qry)
            return False

    #TODO: What do about drawings??
    def load_drawing(self):
        return True

    #TODO: Change to new view to show order data instead of part data
    def load_orders(self):
        qry = QtSql.QSqlQuery()
        data = "Select * from view_items where Part = '%s'" % self.part_number.text()
        if qry.exec_(data):
            mod = QtSql.QSqlQueryModel()
            mod.setQuery(qry)
            self.table_orders.setModel(mod)
            self.table_orders.resizeColumnsToContents()
            return True
        else:
            db_err(qry)
            return False

    def load_bom(self):
        qry = QtSql.QSqlQuery()
        data = "Select * from view_bom where BOM = '%s'" % self.pid
        if qry.exec_(data):
            mod = QtSql.QSqlQueryModel()
            mod.setQuery(qry)
            self.table_bom.setModel(mod)
            self.table_bom.resizeColumnsToContents()
            return True
        else:
            db_err(qry)
            return False