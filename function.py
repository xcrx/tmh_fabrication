from PyQt4 import QtGui, QtCore, uic
import os
import us

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


def load_states():
        states = []
        for state in us.STATES:
            states.append(state.abbr)
        comp = QtGui.QCompleter(states)
        comp.setCaseSensitivity(0)
        return comp


class NewAddress(QtGui.QDialog):
    def __init__(self, cid, parent=None):
        QtGui.QDialog.__init__(self, parent)
        uic.loadUi(os.path.split( __file__ )[0] + '/ui/new_address.ui', self)
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