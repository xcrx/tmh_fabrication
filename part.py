import os
from PyQt4 import QtCore, QtGui, QtSql, uic
from dbConnection import db_err
import function
#TODO: BOM functions
    #Add
    #Remove
    #Change Quantity
#TODO: Edit quantities and status
#TODO: Set up drawing functions
    #Format?
    #Load
    #Display
    #Change
#TODO: Reports
    #Basic info
    #Extended info
    #BOM
    #Order History


class Part(QtGui.QWidget):
    goToOrder = QtCore.pyqtSignal([str])
    goToPart = QtCore.pyqtSignal([str])
    data = []

    def __init__(self, pid, parent=None):
        self.pid = pid

        def connections():
            self.table_orders.doubleClicked.connect(self.go_to_order)
            self.table_bom.doubleClicked.connect(self.bom_functions)
            self.description.editingFinished.connect(self.save_data)
            self.material.editingFinished.connect(self.save_data)
            self.stock.editingFinished.connect(self.save_data)
            self.cost.editingFinished.connect(self.save_data)
            self.has_bom.stateChanged.connect(self.save_data)
            self.cut_time.timeChanged.connect(self.save_data)

        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/part.ui', self)

        if not self.load_part():
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

    def load_part(self):
        qry = QtSql.QSqlQuery()
        data = "Select * from view_parts where `Part ID` = '%s'" % self.pid
        if qry.exec_(data):
            if qry.first():
                self.part_number.setText(qry.value(0).toString())
                self.stock.setText(qry.value(1).toString())
                self.description.setText(qry.value(2).toString())
                self.material.setCompleter(function.load_materials())
                self.material.setText(qry.value(3).toString())
                self.cut_time.setTime(qry.value(4).toTime())
                self.cost.setText(qry.value(5).toString())
                self.data.extend((self.description.text(), self.material.text(), self.stock.text(),
                                 self.cost.text(), self.cut_time.time().toString()))
                if qry.value(6).toString() == '0':
                    self.has_bom.setChecked(False)
                    self.data.append('False')
                else:
                    self.has_bom.setChecked(True)
                    self.data.append('True')

                return True
            else:
                QtGui.QMessageBox.critical(None, "Not Found", "A part matching %s could not be found" % self.pid)
                return False
        else:
            db_err(qry)
            return False

    def load_drawing(self):
        return True

    def load_orders(self):
        qry = QtSql.QSqlQuery()
        data = "Select * from view_part_orders where Part = '%s'" % self.part_number.text()
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

    def save_data(self):
        data = []
        qry = QtSql.QSqlQuery()
        if self.description.text() != "":
            data.append(self.description.text())
            if self.material.text() != "":
                mat_id = "mid"
                mat = "Select id from materials where name='%s'" % self.material.text()
                if qry.exec_(mat):
                    if qry.first():
                        mat_id = qry.value(0).toString()
                    else:
                        text = "Could not find any material matching %s" % self.material.text()
                        QtGui.QMessageBox.critical(None, "Material Not Found", text)
                        self.material.setText(self.data[1])
                else:
                    db_err(qry)
                data.append(self.material.text())
                if self.stock.text() != "":
                    data.append(self.stock.text())
                    if self.cost.text() != "":
                        data.append(self.cost.text())
                        data.append(self.cut_time.time().toString())
                        if self.has_bom.isChecked():
                            data.append('True')
                        else:
                            data.append('False')
                        if data != self.data:
                            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                            self.window().statusBar.showMessage("Saving data...")
                            self.window().repaint()
                            db = QtSql.QSqlDatabase.database('qt_sql_default_connection')
                            if db.transaction():
                                update = ("Update parts set description='{0}',mid={1},bom={2} where id={3}"
                                          ).format(data[0], mat_id, data[5], self.pid)
                                if qry.exec_(update):
                                    update = ("Update parts_detail set cut_time='{0}', stock={1}, cost={2} "
                                              "where pid = {3}").format(data[4], data[2], data[3], self.pid)
                                    if qry.exec_(update):
                                        if db.commit():
                                            self.data = data
                                            self.load_part()
                                        else:
                                            del qry
                                            db.rollback()
                                            text = "There was a problem committing the transaction"
                                            QtGui.QMessageBox.critical(None, "Transaction Error", text)
                                    else:
                                        db_err(qry)
                                        del qry
                                        db.rollback()
                                else:
                                    db_err(qry)
                                    del qry
                                    db.rollback()
                            else:
                                text = "There was a problem starting the transaction"
                                QtGui.QMessageBox.critical(None, "Transaction Error", text)
                    else:
                        QtGui.QMessageBox.critical(self, "Missing Info", "Missing price!")
                else:
                    QtGui.QMessageBox.critical(self, "Missing Info", "Missing stock!")
            else:
                QtGui.QMessageBox.critical(self, "Missing Info", "Missing material!")
        else:
            QtGui.QMessageBox.critical(self, "Missing Info", "Missing description!")
        self.window().statusBar.clearMessage()
        QtGui.QApplication.restoreOverrideCursor()

    def go_to_order(self, index):
        mod = index.model()
        oid = mod.data(mod.index(index.row(), mod.columnCount()-2)).toString()
        self.goToOrder.emit(oid)

    def bom_functions(self, index):
        mod = index.model()
        row = index.row()
        col = index.column()
        if col == 1:
            cur_quantity = mod.data(index).toString()
            new_quantity, ok = QtGui.QInputDialog.getInt(None, "New Quantity", "New Quantity", int(cur_quantity))
            print ok
            if ok:
                print cur_quantity, new_quantity
        else:
            self.goToPart.emit(mod.data(mod.index(row, mod.columnCount()-2)).toString())

    def closeEvent(self, event):
        self.description.editingFinished.disconnect()
        self.material.editingFinished.disconnect()
        self.stock.editingFinished.disconnect()
        self.cost.editingFinished.disconnect()
        self.has_bom.stateChanged.disconnect()
        self.cut_time.timeChanged.disconnect()
        event.accept()