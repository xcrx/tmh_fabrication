import os
from PyQt4 import QtCore, QtGui, QtSql, uic
from new_order import NewOrder
from function import SortableTable


class Orders(QtGui.QWidget):
    goToOrder = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        def connections():
            self.filter.textEdited.connect(self.filter_)
            self.table_orders.doubleClicked.connect(self.go_to_order)
            self.button_new_order.clicked.connect(self.new_order)

        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/orders.ui', self)
        self.placeholder.setParent(None)
        self.table_orders = SortableTable(self)
        self.layout().addWidget(self.table_orders, 0, 0, 1, 4)
        connections()
        self.load_orders()
        
    def load_orders(self):
        old_mod = self.table_orders.model() 
        mod = QtSql.QSqlQueryModel()
        if old_mod is not None:
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
                if text.toLower() in mod.data(mod.index(row, col)).toString().toLower():
                    hide = False
            self.table_orders.setRowHidden(row, hide)

    def new_order(self):
        new_order = NewOrder()
        order_id = None
        while not order_id:
            order_id = new_order.get_data()
        if order_id != "Cancel":
            self.load_orders()
            self.goToOrder.emit(int(order_id))

    def go_to_order(self, index):
        mod = index.model()
        row = index.row()
        col = mod.columnCount()-1
        oid = int(mod.data(mod.index(row, col)).toString())
        self.goToOrder.emit(oid)
