from PyQt4 import QtCore, QtGui, QtSql, uic
from function import lineCalendar, get_address, get_addresses, NewAddress
from dbConnection import dbErr
import os


class NewOrder(QtGui.QDialog):

    def __init__(self, parent=None):
        def connections():
            self.button_cancel.clicked.connect(self.reject)
            self.button_new_order.clicked.connect(self.accept)
            self.customer.currentIndexChanged.connect(self.change_customer)
            self.s_address1.currentIndexChanged["QString"].connect(self.change_address)
            self.b_address1.currentIndexChanged["QString"].connect(self.change_address)
            self.priority_slider.sliderMoved.connect(self.update_digit)
            self.priority_digit.textEdited.connect(self.update_slider)

        QtGui.QDialog.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/new_order.ui', self)
        self.due_date = lineCalendar()
        self.due_date.setObjectName("due_date")
        self.ordered_date = lineCalendar()
        self.ordered_date.setObjectName("ordered_date")
        self.order_layout.addWidget(self.ordered_date, 1, 1)
        self.ordered_date.setDate(QtCore.QDateTime.currentDateTime())
        self.order_layout.addWidget(self.due_date, 2, 1)
        priority = self.priority_slider.value()
        self.priority_digit.setText(str(priority))
        ok = self.get_customers()
        if not ok:
            self.close()

        connections()

    def get_customers(self):
        qry = QtSql.QSqlQuery()
        data = "Select name, id from customers"
        if qry.exec_(data):
            mod = QtSql.QSqlQueryModel()
            mod.setQuery(qry)
            self.customer.setModel(mod)
            return True
        else:
            dbErr(qry)
            QtGui.QMessageBox.critical(None, "Fatal Error", "Failed to load customers from database. Aborting!")
            return False

    def change_customer(self, index):
        if index > 0:
            self.tabs.setEnabled(True)
        else:
            self.tabs.setEnabled(False)

        mod = self.customer.model()
        self.customer = mod.data(mod.index(index, 1)).toString()
        self.s_address1.clear()
        self.b_address1.clear()
        addresses = get_addresses(self.customer)
        self.s_address1.addItems(addresses)
        self.b_address1.addItems(addresses)
        self.s_address1.setCurrentIndex(0)
        self.b_address1.setCurrentIndex(0)

    def change_address(self, address):
        sender = self.sender()
        if address == "":
            return False
        if address == "Add New Address...":
            stat = self.new_address_()
            if not stat:
                return False
            self.s_address1.clear()
            self.b_address1.clear()
            addresses = get_addresses(self.customer)
            self.s_address1.addItems(addresses)
            self.b_address1.addItems(addresses)
            self.s_address1.setCurrentIndex(self.s_address1.findText(stat))
            return
        else:
            qry = QtSql.QSqlQuery()
            data = "Select id from customer_addresses where cid={0} and address1='{1}'".format(self.customer, address)
            if qry.exec_(data):
                if qry.first():
                    aid = qry.value(0).toString()
                else:
                    QtGui.QMessageBox.critical(None, "Database Error", "Couldn't find address like %s" % address)
                    return False
            else:
                dbErr(qry)
                return False
        address = get_address(self.customer, aid)
        if sender.objectName() == "s_address1":
            self.s_address2.setText(address[1])
            self.s_city.setText(address[2])
            self.s_state.setText(address[3])
            self.s_zipcode.setText(address[4])
        elif sender.objectName() == "b_address1":
            self.b_address2.setText(address[1])
            self.b_city.setText(address[2])
            self.b_state.setText(address[3])
            self.b_zipcode.setText(address[4])
        else:
            text = "A signal to change the address came from an unknown source. Aliens??"
            QtGui.QMessageBox.critical(None, "Unknown Sender", text)
            return False

    def new_address_(self):
        new_address = NewAddress(self)
        address = False
        while not address:
            address = new_address.get_data()
        if address == "Cancel":
            return False
        qry = QtSql.QSqlQuery()
        data = ("Insert into customer_addresses (id, cid, address1, address2, city, state, zip) Values((select max(id) "
                "from customer_addresses as s where cid = '{0}')+1, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')"
                ).format(self.customer, *address)
        if qry.exec_(data):
            return address[0]
        else:
            dbErr(qry)
            return False

    def get_data(self):
        ok = self.exec_()
        if ok:
            oid = self.insert_new_order()
            if oid:
                return oid
            else:
                return False
        else:
            return "Cancel"

    def update_digit(self, value):
        if self.priority_digit.text() != str(value):
            self.priority_digit.setText(str(value))

    def update_slider(self, value):
        if str(self.priority_slider.value()) != value and value != "":
            self.priority_slider.setValue(int(value))

    def insert_new_order(self):
        values = [self.customer]
        qry = QtSql.QSqlQuery()
        address = self.s_address1.currentText()
        data = ("Select id from customer_addresses where cid={0} and address1='{1}'"
                ).format(self.customer, address)
        if qry.exec_(data):
            if qry.first():
                s_aid = qry.value(0).toString()
            else:
                QtGui.QMessageBox.critical(None, "Database Error", "Couldn't find address like %s" % address)
                return False
        address = self.b_address1.currentText()
        data = ("Select id from customer_addresses where cid={0} and address1='{1}'"
                ).format(self.customer, address)
        if qry.exec_(data):
            if qry.first():
                b_aid = qry.value(0).toString()
            else:
                QtGui.QMessageBox.critical(None, "Database Error", "Couldn't find address like %s" % address)
                return False
        values.append(s_aid)
        values.append(b_aid)
        values.append(self.po_number.text())
        values.append(self.ordered_date.text())
        values.append(self.due_date.text())
        for d in data:
            if d == "" or d is None:
                QtGui.QMessageBox.critical(None, "Incomplete Data", "You must fill out all required data!")
        trans = QtSql.QSqlDatabase.database('qt_sql_default_connection')
        data = ("Insert into orders (cid, shipping, billing, po, odate, ddate) "
                "Values({0},{1},{2},'{3}','{4}','{5}')").format(*values)
        if trans.transaction():
            trans_qry = QtSql.QSqlQuery(trans)
            if trans_qry.exec_(data):
                oid = qry.lastInsertId().toString()
                note = self.notes.toPlainText()
                data = "Insert into orders_note (oid, notes) VALUES({0}, '{1}')".format(oid, note)
                if trans_qry.exec_(data):
                    pdig = self.priority_digit.text()
                    data = "Insert into orders_status (oid, priority) VALUES({0}, {1})".format(oid, pdig)
                    if trans_qry.exec_(data):
                        trans_qry.finish()
                        del trans_qry
                        if trans.commit():
                            QtGui.QMessageBox.information(None, "Successful", "%s has been inserted" % oid)
                            return oid
                        else:
                            trans.rollback()
                            text = "There was an error committing the transaction"
                            QtGui.QMessageBox.critical(None, "Commit Error", text)
                    else:
                        print data
                        trans.rollback()
                        dbErr(trans_qry)
                else:
                    print data
                    trans.rollback()
                    dbErr(trans_qry)
            else:
                print data
                trans.rollback()
                dbErr(trans_qry)
        else:
            dbErr(trans)
            QtGui.QMessageBox.critical(None, "Transaction Error", "There was an error starting the transaction")