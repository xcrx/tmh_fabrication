import os
from PyQt4 import QtCore, QtGui, QtSql, uic
from dbConnection import db_err
import function


class Order(QtGui.QWidget):
    goToPart = QtCore.pyqtSignal([str])
    toolbar1 = None
    cid = str

    def __init__(self, oid, parent=None):

        def connections():
            self.discount.textEdited.connect(self.data_edited)
            self.due_date.textEdited.connect(self.data_edited)
            self.po_number.textEdited.connect(self.data_edited)
            self.notes.focusOutEvent = self.note_edited
            self.action_finished.triggered.connect(self.order_finished)
            self.action_delete.triggered.connect(self.order_delete)
            self.s_address1.currentIndexChanged['QString'].connect(self.change_address)
            self.b_address1.currentIndexChanged['QString'].connect(self.change_address)
            self.processing.clicked.connect(self.set_processing)
            self.add_part.clicked.connect(self.add_part_)
            self.table_items.doubleClicked.connect(self.item_functions)

        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/order.ui', self)
        self.due_date = function.LineCalendar()
        self.due_date.setObjectName("due_date")
        self.order_layout.addWidget(self.due_date, 4, 1)
        self.load_actions()
        connections()
        self.load_order(oid)
        title = "{0} - {1}".format(self.customer.text(), self.order_id.text())
        self.setWindowTitle(title)
        self.parts_completer()
    
    def load_actions(self):
        self.toolbar1 = QtGui.QToolBar("Order")
        self.toolbar1.addActions([self.action_invoice, self.action_list,
                                  self.action_delete, self.action_finished]
                                 )
        self.parent().addToolBar(self.toolbar1)
    
    def load_order(self, oid):
        qry = QtSql.QSqlQuery()
        select = "Select * from view_order where Id = %s" % oid
        if qry.exec_(select):
            if qry.first():
                rec = qry.record()
                values = []
                for i in range(rec.count()):
                    values.append(qry.value(i).toString())
                    
                self.order_id.setText(values[0])
                self.po_number.setText(values[1])
                self.ordered_date.setText(values[2])
                self.due_date.setText(values[3])
                self.notes.setPlainText(values[5])
                self.discount.setText(values[6])
                self.customer.setText(values[7])
                if values[4] == '0':
                    self.processing.setChecked(False)
                else:
                    self.processing.setChecked(True)
                self.load_addresses(oid)
                self.load_items(oid)
            else:
                text = "No order could be found for %s" % oid
                QtGui.QMessageBox.critical(None, "No Order", text)
                self.close()
        else:
            print select
            db_err(qry)
            self.close()
            
    def load_addresses(self, cid):
        qry = QtSql.QSqlQuery()
        select = "Select cid, shipping, billing from orders where id = %s" % cid
        if qry.exec_(select):
            if qry.first():
                self.cid = qry.value(0).toString()
                shipping_id = qry.value(1).toString()
                shipping = []
                billing_id = qry.value(2).toString()
                billing = []
                self.s_address1.currentIndexChanged['QString'].disconnect()
                self.b_address1.currentIndexChanged['QString'].disconnect()
                self.s_address1.clear()
                self.b_address1.clear()
                addresses = function.get_addresses(self.cid)
                for address in addresses:
                    self.s_address1.addItem(address[0])
                    self.b_address1.addItem(address[0])
                    if address[1] == shipping_id:
                        shipping = function.get_address(self.cid, address[0])
                    if address[1] == billing_id:
                        billing = function.get_address(self.cid, address[0])
                self.s_address1.setCurrentIndex(self.s_address1.findText(shipping[0]))
                self.s_address2.setText(shipping[1])
                self.s_city.setText(shipping[2])
                self.s_state.setText(shipping[3])
                self.s_zipcode.setText(shipping[4])
                self.b_address1.setCurrentIndex(self.b_address1.findText(billing[0]))
                self.b_address2.setText(billing[1])
                self.b_city.setText(billing[2])
                self.b_state.setText(billing[3])
                self.b_zipcode.setText(billing[4])
                self.s_address1.currentIndexChanged['QString'].connect(self.change_address)
                self.b_address1.currentIndexChanged['QString'].connect(self.change_address)
                return True
            else:
                text = "Couldn't find on order that matched %s" % cid
                QtGui.QMessageBox.critical(None, "No Order", text)
                return False
        else:
            db_err(qry)
            return False

    def change_address(self, address):
        if address == "":
            return False
        sender = self.sender().objectName()
        if address == "Add New Address...":
            stat = self.new_address_()
            if not stat:
                return False
            qry = QtSql.QSqlQuery()
            if qry.exec_("Select max(id) from customer_addresses where cid ='%s'" % self.cid):
                qry.first()
                a_id = qry.value(0).toString()
            else:
                db_err(qry)
                return False
        else:
            qry = QtSql.QSqlQuery()
            data = "Select id from customer_addresses where cid={0} and address1='{1}'".format(self.cid, address)
            if qry.exec_(data):
                if qry.first():
                    a_id = qry.value(0).toString()
                else:
                    QtGui.QMessageBox.critical(None, "Database Error", "Couldn't find address like %s" % address)
                    return False
            else:
                db_err(qry)
                return False

        if sender == "s_address1":
            data = "update orders set shipping={0} where id={1}".format(a_id, self.order_id.text())
        elif sender == "b_address1":
            data = "update orders set billing={0} where id={1}".format(a_id, self.order_id.text())
        else:
            text = "A signal to change the address came from an unknown source. Aliens??"
            QtGui.QMessageBox.critical(None, "Unknown Sender", text)
            return False
        qry = QtSql.QSqlQuery()
        if qry.exec_(data):
            self.load_addresses(self.order_id.text())
        else:
            db_err(qry)

    def new_address_(self):
        new_address = function.NewAddress(self)
        address = False
        while not address:
            address = new_address.get_data()
        if address == "Cancel":
            return False
        qry = QtSql.QSqlQuery()
        data = ("Insert into customer_addresses (id, cid, address1, address2, city, state, zip) Values((select max(id) "
                "from customer_addresses as s where cid = '{0}')+1, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')"
                ).format(self.cid, *address)
        if qry.exec_(data):
            return True
        else:
            db_err(qry)
            return False

    def load_items(self, iid):
        qry = QtSql.QSqlQuery()
        select = "Select * from view_items where `Order #` = %s" % iid
        if qry.exec_(select):
            mod = QtSql.QSqlQueryModel()
            mod.setQuery(qry)
            self.table_items.setModel(mod)
            self.table_items.resizeColumnsToContents()
        else:
            db_err(qry)

    def item_functions(self, index):
        mod = index.model()
        col = index.column()
        row = index.row()
        if col == 0:
            pid = function.get_part_id(mod.data(mod.index(row, col)).toString())
            self.goToPart.emit(pid)
        elif col == 1:
            self.update_item_qty(mod.record(row))
        elif col == 2:
            self.update_item_status(mod.record(row))
        elif col == 3:
            self.update_item_stock(mod.record(row))
        elif col == 4:
            self.update_item_desc(mod.record(row))
        elif col == 5:
            self.update_item_material(mod.record(row))

    def update_item_qty(self, record):
        iid = record.value("id").toString()
        oid = self.order_id.text()
        old_qty = record.value("Ordered").toString()
        new_qty, ok = QtGui.QInputDialog.getInt(None, "Quantity", "", int(old_qty))
        if ok and new_qty != old_qty:
            qry = QtSql.QSqlQuery()
            data = "Update items set quantity=%d where id=%s" % (new_qty, iid)
            if qry.exec_(data):
                self.load_items(oid)
            else:
                db_err(qry)

    def update_item_status(self, record):
        iid = record.value("id").toString()
        oid = self.order_id.text()
        old_status = record.value("Status").toString()
        new_status, ok = QtGui.QInputDialog.getText(None, "New Status", "")
        if ok and new_status != old_status:
            qry = QtSql.QSqlQuery()
            data = "Insert into item_status (iid, status) VALUES(%s,'%s')" % (iid, new_status)
            if qry.exec_(data):
                self.load_items(oid)
            else:
                db_err(qry)

    def update_item_stock(self, record):
        iid = record.value("id").toString()
        oid = self.order_id.text()
        old_stock = record.value("Stock").toString()
        new_stock, ok = QtGui.QInputDialog.getInt(None, "Stock Quantity", "", int(old_stock))
        if ok and new_stock != old_stock:
            qry = QtSql.QSqlQuery()
            data = "Select pid from items where id=%s" % iid
            if qry.exec_(data):
                if qry.first():
                    pid = qry.value(0).toString()
                else:
                    QtGui.QMessageBox.critical(None, "Error", "Could not find part related to %s" % iid)
                    return False
            else:
                db_err(qry)
                return False
            data = "Update parts_detail set stock=%d where pid=%s" % (new_stock, pid)
            if qry.exec_(data):
                self.load_items(oid)
            else:
                db_err(qry)

    def update_item_desc(self, record):
        iid = record.value("id").toString()
        oid = self.order_id.text()
        old_desc = record.value("Description").toString()
        new_desc, ok = QtGui.QInputDialog.getText(None, "Description", "", 0, old_desc)
        if ok and new_desc != old_desc:
            qry = QtSql.QSqlQuery()
            data = "Select pid from items where id=%s" % iid
            if qry.exec_(data):
                if qry.first():
                    pid = qry.value(0).toString()
                else:
                    QtGui.QMessageBox.critical(None, "Error", "Could not find part related to %s" % iid)
                    return False
            else:
                db_err(qry)
                return False
            data = "Update parts set description='%s' where id=%s" % (new_desc, pid)
            if qry.exec_(data):
                self.load_items(oid)
            else:
                db_err(qry)

    def update_item_material(self, record):
        iid = record.value("id").toString()
        oid = self.order_id.text()
        old_material = record.value("Material").toString()
        qry = QtSql.QSqlQuery()
        data = "Select name from materials"
        if qry.exec_(data):
            materials = []
            while qry.next():
                materials.append(qry.value(0).toString())
        else:
            db_err(qry)
            return False
        new_material, ok = QtGui.QInputDialog.getItem(None, "Material", "", materials)
        if ok and new_material != old_material:
            data = "Select pid from items where id=%s" % iid
            if qry.exec_(data):
                if qry.first():
                    pid = qry.value(0).toString()
                else:
                    QtGui.QMessageBox.critical(None, "Error", "Could not find part related to %s" % iid)
                    return False
            else:
                db_err(qry)
                return False
            data = "Select id from materials where name='%s'" % new_material
            if qry.exec_(data):
                if qry.first():
                    mid = qry.value(0).toString()
                else:
                    QtGui.QMessageBox.critical(None, "Error", "Could not find material related to %s" % new_material)
                    return False
            else:
                db_err(qry)
                return False
            data = "Update parts set mid=%s where id=%s" % (mid, pid)
            if qry.exec_(data):
                self.load_items(oid)
            else:
                db_err(qry)

    def parts_completer(self):
        qry = QtSql.QSqlQuery()
        data = "Select part from parts order by part"
        if qry.exec_(data):
            parts = []
            while qry.next():
                parts.append(qry.value(0).toString())
            comp = QtGui.QCompleter(parts)
            comp.setCaseSensitivity(0)
            self.part_number.setCompleter(comp)
    
    def order_finished(self):
        oid = self.order_id.text()
        confirm = QtGui.QMessageBox.question(self, "Confirm Finished", "Are you sure you want to finish order %s?" % oid,
                                             "No", "Yes", defaultButtonNumber=1, escapeButtonNumber=0)
        if confirm == 1:
            data = ("Update orders_status set processing='0', finished = '-1'"
                    "where oid={0}").format(oid)
            qry = QtSql.QSqlQuery()
            if qry.exec_(data):
                text = "{0} was marked as finished".format(oid)
                QtGui.QMessageBox.information(None, "Finished", text)
                self.close()
                self.update_data.emit()
            else:
                db_err(qry)
    
    def order_delete(self):
        id = self.order_id.text()
        confirm = QtGui.QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete order %s?" % id,
                                             "No", "Yes", defaultButtonNumber=1, escapeButtonNumber=0)
        if confirm == 1:
            data = "Delete from orders where id = %s" % id
            qry = QtSql.QSqlQuery()
            if qry.exec_(data):
                text = "{0} was deleted".format(id)
                QtGui.QMessageBox.information(None, "Finished", text)
                self.update_data.emit()
                self.close()
            else:
                db_err(qry)
                return False
        else:
            return False

    def add_part_(self):
        part = self.part_number.text()
        oid = self.order_id.text()
        qry = QtSql.QSqlQuery()
        data = "Select id from parts where part='%s'" % part
        if qry.exec_(data):
            if qry.first():
                qty, ok = QtGui.QInputDialog.getInt(self, "Quantity", "", 1)
                if ok and qty > 0:
                    pid = qry.value(0).toString()
                    data = "Insert into items (oid, pid, quantity) VALUES(%s,%s,%s)" % (oid, pid, qty)
                    if qry.exec_(data):
                        self.part_number.setText("")
                        self.load_items(oid)
                    else:
                        self.part_number.setText("")
                        db_err(qry)
                else:
                    self.part_number.setText("")
            else:
                QtGui.QMessageBox.critical(None, "Not Found", "Could not find part matching %s!" % part)
        else:
            db_err(qry)

    def set_processing(self):
        state = self.processing.checkState()
        if state:
            processing = -1
        else:
            processing = 0
        id = self.order_id.text()
        qry = QtSql.QSqlQuery()
        data = "Update orders_status set processing={0} where oid={1}".format(processing, id)
        if qry.exec_(data):
            self.load_order(id)
        else:
            db_err(qry)

    def data_edited(self):
        data_map = [["discount", "orders_discount", "cost", "oid"],
               ["due_date", "orders", "ddate", "id"],
               ["po_number", "orders", "po", "id"], ]
        
        oid = self.order_id.text()
        
        data = self.sender().objectName()
        key = None
        for value in data_map:
            if value[0] == data:
                key = value
        if key is not None:
            text = self.sender().text()
            qry = QtSql.QSqlQuery()
            update = ("Update {0} set {1} = '{2}' where {3} = '{4}'"
                      ).format(key[1], key[2], text, key[3], oid)
            if qry.exec_(update):
                self.load_order(oid)
            else:
                db_err(qry)
    
    def note_edited(self, event):
        oid = self.order_id.text()
        text = self.notes.toPlainText()
        qry = QtSql.QSqlQuery()
        update = ("Update orders_note set notes = '{0}' where oid = {1}"
                  ).format(text, oid)
        if qry.exec_(update):
            self.load_order(oid)
        else:
            db_err(qry)
        event.accept()
            
    def closeEvent(self, event):
        self.toolbar1.close()
        del self.toolbar1
        event.accept()