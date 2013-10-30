from PyQt4 import QtCore, QtGui, QtSql, uic


class NewPart(QtGui.QDialog):

    def __init__(self, parent=None):
        def connections():
            pass

        QtGui.QDialog.__init__(self, parent)
        #uic.loadUi(os.path.split(__file__)[0] + '/ui/new_part.ui', self)
        connections()

    def get_data(self):
        ok = self.exec_()
        if ok:
            return True
        else:
            return "Cancel"

    def insert_new_order(self):
        pass