import sys
import os

from PyQt4 import QtGui, QtCore, uic
from orders import Orders
from order import Order
from parts import Parts
from part import Part
from dbConnection import default_connection
from function import TMHSettings


#noinspection PyCallByClass
class Main(QtGui.QMainWindow):
    def __init__(self, parent=None):
        self.toolbar1 = QtGui.QToolBar('Files')

        def connections():
            self.action_orders.triggered.connect(self.view_orders)
            self.action_parts.triggered.connect(self.view_parts)
            
        QtGui.QMainWindow.__init__(self, parent)
        uic.loadUi(os.path.split(__file__)[0] + '/ui/main.ui', self)
        self.resize(TMHSettings().read("size", QtCore.QSize(400, 400)).toSize())
        self.move(TMHSettings().read("pos", QtCore.QPoint(200, 200)).toPoint())
        connections()
        self.create_actions()
        
    def create_actions(self):
        self.toolbar1.addActions([self.action_orders, self.action_parts,
                                  self.action_customers, self.action_materials]
                                 )
        
        self.addToolBar(self.toolbar1)

    def new_sub_window(self, module, icon=":icons/appLogo.png", args=None):
        """
        Creates and returns a new new subwindow for the mdi area.
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
            QtGui.QMessageBox.critical(None, "Failed to Create Sub-Window", str(e))
            sub = None
            stat = False
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        return sub, stat
        
    ####Subwindow definitions
    def view_orders(self):
        orders, ok = self.new_sub_window(Orders)
        if ok:
            orders_widget = orders.widget()
            orders_widget.goToOrder.connect(self.view_order)
    
    def view_order(self, oid):
        order, ok = self.new_sub_window(Order, args=oid)
        if ok:
            order_widget = order.widget()
            order_widget.goToPart.connect(self.view_part)

    def view_parts(self):
        parts, ok = self.new_sub_window(Parts)
        if ok:
            parts_widget = parts.widget()
            parts_widget.goToPart.connect(self.view_part)

    def view_part(self, pid):
        part, ok = self.new_sub_window(Part, args=pid)
        if ok:
            part_widget = self.part.widget()
            part_widget.goToPart.connect(self.view_part)
            part_widget.goToOrder.connect(self.view_order)

    def closeEvent(self, event):
        TMHSettings().write("size", self.size())
        TMHSettings().write("pos", self.pos())
        event.accept()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    if not default_connection():
        sys.exit(1)
    my_app = Main()
    my_app.show()
    sys.exit(app.exec_())
