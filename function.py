from PyQt4 import QtGui, QtCore, QtSql, uic
import os
import us
import re
import pyzipcode
from dbConnection import db_err


class LineCalendar(QtGui.QLineEdit):
    """
    This is a lineEdit object with a pop-up calendar for easier editing.
    """
    cal = None

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setInputMask('####-##-##')  # Holds the field to a date format.
        self.setText('0000-00-00')
        self.mousePressEvent = self.calendar
        self.setup_calendar()
        
    def setup_calendar(self):
        """
        This is the widget for the pop-up
        """
        self.cal = QtGui.QCalendarWidget()
        self.cal.setWindowFlags(QtCore.Qt.Popup)
        self.cal.hide()
        self.cal.activated.connect(self.set_date)
        
    def calendar(self, event):
        """
        Show/Hide the pop-up
        """
        if self.cal.isVisible():
            self.cal.hide()
        else:
            self.cal_pos()
            self.cal.show()
        event.accept()
    
    def cal_pos(self):
        """
        Finds the position of the lineEdit and opens the
        popup underneath it.
        """
        le_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
        le_h = self.height()
        pos = QtCore.QPoint()
        pos.setX(le_pos.x())
        pos.setY(le_pos.y()+le_h)
        self.cal.move(pos)
        
    def set_date(self, date):
        """
        Takes the date from the pop-up and converts it to a
        string and sets to the lineEdit
        """
        if not self.isReadOnly():
            self.setText(date.toString("yyyy-MM-dd"))
            self.textEdited.emit(date.toString("yyyy-MM-dd"))
            self.editingFinished.emit()
        self.cal.hide()


def load_states():
    states = []
    for state in us.STATES:
        states.append(state.abbr)
    comp = QtGui.QCompleter(states)
    comp.setCaseSensitivity(0)
    return comp


def zip_lookup(zipcode):
    zip_db = pyzipcode.ZipCodeDatabase()
    try:
        zip_data = zip_db[zipcode]
    except IndexError:
        return False, False
    city = zip_data.city
    state = zip_data.state
    return city, state


def load_materials():
    materials = []
    qry = QtSql.QSqlQuery()
    data = "Select name from materials order by name"
    if qry.exec_(data):
        while qry.next():
            materials.append(qry.value(0).toString())
    else:
        db_err(qry)
    comp = QtGui.QCompleter(materials)
    comp.setCaseSensitivity(0)
    return comp


def get_addresses(cid):
    qry = QtSql.QSqlQuery()
    data = "Select address1, id from customer_addresses where cid=%s" % cid
    addresses = []
    if qry.exec_(data):
        while qry.next():
            addresses.append([qry.value(0).toString(), qry.value(1).toString()])
        addresses.append(["Add New Address...", "99"])
        return addresses
    else:
        db_err(qry)
        return False


def get_part_id(part_num):
    qry = QtSql.QSqlQuery()
    data = "Select id from parts where part = '%s'" % part_num
    if qry.exec_(data):
        if qry.first():
            return qry.value(0).toString()
        else:
            QtGui.QMessageBox.critical(None, "Not Found", "Could not find a part related to %s" % part_num)
            return None
    else:
        db_err(qry)
        return None


def get_address(cid, street):
    qry = QtSql.QSqlQuery()
    select = ("Select address1, address2, city, state, zip from customer_addresses "
              "where cid = %s and address1 = '%s'" % (cid, street))
    if qry.exec_(select):
        qry.first()
        address = []
        for i in range(5):
            address.append(qry.value(i).toString())
        return address
    else:
        db_err(qry)
        return []


class NewAddress(QtGui.QDialog):
    def __init__(self, cid, parent=None):
        QtGui.QDialog.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/new_address.ui', self)
        state_comp = load_states()
        self.state.setCompleter(state_comp)
        self.cid = cid
        self.button_cancel.clicked.connect(self.reject)
        self.button_accept.clicked.connect(self.accept)
        self.zipcode.textEdited.connect(self.get_zip_data)

    def get_zip_data(self, zipcode):
        city, state = zip_lookup(zipcode)
        if city and state:
            if self.city.text() == "":
                self.city.setText(city)
            if self.state.text() == "":
                self.state.setText(state)

    def get_data(self):
        ok = self.exec_()
        if ok:
            address = [self.address1.text(), self.address2.text(), self.city.text(),
                       self.state.text(), self.zipcode.text()]
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


class TMHSettings(QtCore.QSettings):
    def __init__(self, form=1, scope=0, organization='TMH Fabrication', app='Inventory Control', parent=None):
        QtCore.QSettings.__init__(self, form, scope, organization,  app, parent)

    def read(self, key, value=None, group="Main"):
        self.sync()
        stat = self.status()
        if stat == 0:
            self.beginGroup(group)
            data = self.value(key, value)
            self.endGroup()
            return data
        elif stat == 1:
            QtGui.QMessageBox.critical(None, "Access Error", "Could not read setting from %s" % self.organizationName())
            return None
        elif stat == 2:
            QtGui.QMessageBox.critical(None, "Format Error", "INI file appears to be corrupt. :(")
            return None

    def write(self, key, value, group="Main"):
        self.beginGroup(group)
        self.setValue(key, value)
        self.endGroup()
        self.sync()
        stat = self.status()
        if stat == 0:
            return True
        elif stat == 1:
            QtGui.QMessageBox.critical(None, "Access Error", "Could not write settings to %s" % self.organizationName())
            return False
        elif stat == 2:
            QtGui.QMessageBox.critical(None, "Format Error", "INI file appears to be corrupt. :(")
            return False


class SortableTable(QtGui.QTableView):
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)
        self.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)

    def sort_table(self, index, order):
        if order:
            order = " Desc"
        else:
            order = " Asc"
        mod = self.model()
        column = mod.headerData(index, 1).toString()
        data = mod.query().lastQuery()
        if "ORDER BY" in data:
            data = re.sub("ORDER BY .*", "ORDER BY `%s` %s" % (column, order), str(data), 99)
        else:
            data += " ORDER BY `%s` %s" % (column, order)
        mod.setQuery(data)
        mod.query().exec_()