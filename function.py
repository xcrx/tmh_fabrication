from PyQt4 import QtGui, QtCore, QtSql, uic
import os
import us
from dbConnection import dbErr

class lineCalendar(QtGui.QLineEdit):
    '''This is a lineEdit object with a pop-up calendar for easier editing.
    '''
    def __init__(self, parent=None):            
        QtGui.QLineEdit.__init__(self, parent)
        self.setInputMask('####-##-##')  # Holds the field to a date format.
        self.setText('0000-00-00')
        self.mousePressEvent = self.calendar
        self.setupCalendar()
        
    def setupCalendar(self):
        '''This is the widget for the pop-up
        '''
        self.cal = QtGui.QCalendarWidget()
        self.cal.setWindowFlags(QtCore.Qt.Popup)
        self.cal.hide()
        self.cal.activated.connect(self.setDate)
        
    def calendar(self, event):
        '''Show/Hide the pop-up
        '''
        if self.cal.isVisible():
            self.cal.hide()
        else:
            self.calPos()
            self.cal.show()
    
    def calPos(self):
        '''Finds the position of the lineEdit and opens the 
        popup underneath it.
        '''
        lePos = self.mapToGlobal(QtCore.QPoint(0,0))
        leH = self.height()
        pos = QtCore.QPoint()
        pos.setX(lePos.x())
        pos.setY(lePos.y()+leH)
        self.cal.move(pos)
        
    def setDate(self, date):
        '''Takes the date from the pop-up and converts it to a 
        string and sets to the lineEdit
        '''
        if not self.isReadOnly():
            self.setText(date.toString("yyyy-MM-dd"))
            self.textEdited.emit(date.toString("yyyy-MM-dd"))
            self.editingFinished.emit()
        self.cal.hide()

#TODO: Create similar to lookup city and state by zip
def load_states():
    states = []
    for state in us.STATES:
        states.append(state.abbr)
    comp = QtGui.QCompleter(states)
    comp.setCaseSensitivity(0)
    return comp


def get_addresses(cid):
    qry = QtSql.QSqlQuery()
    data = "Select address1 from customer_addresses where cid=%s" % cid
    addresses = []
    if qry.exec_(data):
        while qry.next():
            addresses.append(qry.value(0).toString())
        addresses.append("Add New Address...")
        return addresses
    else:
        dbErr(qry)
        return False


def get_address(cid, aid):
        qry = QtSql.QSqlQuery()
        select = ("Select address1, address2, city, state, zip from "
                  "customer_addresses where cid = %s and id = %s" % (cid, aid))
        if qry.exec_(select):
            qry.first()
            address = []
            for i in range(5):
                address.append(qry.value(i).toString())
            return address
        else:
            dbErr(qry)
            return False


class NewOrder(QtGui.QDialog):
    def __init__(self, parent=None):
        def connections():
            self.button_cancel.clicked.connect(self.reject)
            self.button_new_order.clicked.connect(self.accept)
            self.customer.currentIndexChanged.connect(self.change_customer)
            self.s_address1.currentIndexChanged["QString"].connect(self.change_address)
            self.b_address1.currentIndexChanged["QString"].connect(self.change_address)

        QtGui.QDialog.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/new_order.ui', self)
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
            return True
        else:
            return "Cancel"


class NewAddress(QtGui.QDialog):
    def __init__(self, cid, parent=None):
        QtGui.QDialog.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/new_address.ui', self)
        state_comp = load_states()
        self.state.setCompleter(state_comp)
        self.cid = cid
        self.button_cancel.clicked.connect(self.reject)
        self.button_accept.clicked.connect(self.accept)

    def get_data(self):
        ok = self.exec_()
        if ok:
            address = [self.address1.text(), self.address2.text(), self.city.text(), self.state.text(), self.zipcode.text()]
            if address[0] != "":
                if address[2] != "":
                    if address[3] != "":
                        if address[4] != "":
                            return address
                        else:
                            QtGui.QMessageBox.critical(None, "Missing Data", "Zip Code Required")
                    else:
                        QtGui.QMessageBox.critical(None, "Missing Data", "State Required")
                else:
                    QtGui.QMessageBox.critical(None, "Missing Data", "City Required")
            else:
                QtGui.QMessageBox.critical(None, "Missing Data", "Street Address Required")
            return False
        else:
            return "Cancel"