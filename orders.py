import sys, os
from PyQt4 import QtCore, QtGui, QtSql, uic

class orders(QtGui.QWidget):
    goToOrder = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        def connections():
            self.filter.textEdited.connect(self.filter_)
            self.table_orders.doubleClicked.connect(self.goToOrder_)

        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(os.path.split( __file__ )[0] + '/ui/orders.ui', self)
        connections()
        self.load_orders()
        
    def load_orders(self, pos=0):
        old_mod = self.table_orders.model() 
        mod = QtSql.QSqlQueryModel()
        if old_mod != None:
            pos = self.table_orders.currentIndex()
        else:
            pos = mod.index(0, 0)
        mod.setQuery('select * from view_orders')
        self.table_orders.setModel(mod)
        self.table_orders.setCurrentIndex(pos)
        self.table_orders.resizeColumnsToContents()
            
    def filter_(self, text):
        mod = self.table_orders.model()
        rows = mod.rowCount()
        cols = mod.columnCount()
        for row in range(rows):
            hide = True
            for col in range(cols):
                if text.toLower() in mod.data(mod.index(row,col)).toString().toLower():
                    hide = False
            self.table_orders.setRowHidden(row, hide)
            
    def goToOrder_(self, index):
        mod = index.model()
        row = index.row()
        col = mod.columnCount()-1
        id = int(mod.data(mod.index(row, col)).toString())
        self.goToOrder.emit(id)
