import sys
import os
from PyQt4 import QtGui, QtCore, QtSql, uic
from orders import Orders
from order import Order
from dbConnection import defaultConnection, dbErr


class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        def connections():
            self.action_orders.triggered.connect(self.view_orders)
            
        QtGui.QMainWindow.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/main.ui', self)
        connections()
        self.actions()
        
    def actions(self):
        self.toolbar1 = QtGui.QToolBar('Files')
        self.toolbar1.addActions([self.action_orders, self.action_parts,
                                  self.action_customers, self.action_materials]
                                 )
        
        self.addToolBar(self.toolbar1)
    
    def new_sub_window(self, module, icon=":icons/appLogo.png", args=None):
        """Creates and returns a new new subwindow for the mdi area.
        'module' is the class that should be used to create the new subwindow.
        """
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            if args is None:
                mod = module(parent=self)
            else:
                mod = module(args, parent=self)
            sub = self.mdiArea.addSubWindow(mod)
            stat = True
            sub.setWindowIcon(QtGui.QIcon(icon))
            sub.showMaximized()
        except AttributeError as e:
            QtGui.QMessageBox.critical(self, "Failed to Create Sub-Window", str(e))
            sub = None
            stat = False
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        return sub, stat
        
####Subwindow definitions
    def view_orders(self):
        self.orders, exit = self.new_sub_window(Orders)
        if exit:
            self.orders_widget = self.orders.widget()
            self.orders_widget.goToOrder.connect(self.view_order)
    
    def view_order(self, id):
        self.order, exit = self.new_sub_window(Order, args=id)
        if exit:
            self.order_widget = self.order.widget()
            self.order_widget.update_data.connect(self.orders_widget.load_orders)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    if not defaultConnection():
        sys.exit(1)
    my_app = Main()
    my_app.show()
    sys.exit(app.exec_())
