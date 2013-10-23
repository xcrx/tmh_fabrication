from PyQt4 import QtCore, QtGui, QtSql


def defaultConnection():
    QtSql.QSqlDatabase.database('qt_sql_default_connection').close()
    QtSql.QSqlDatabase.removeDatabase('qt_sql_default_connection')
    db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
    db.setUserName('rhanson')
    passwd, exit = QtGui.QInputDialog.getText(None, 'Enter Password', 'Password', 2)
    db.setPassword(passwd)
    db.setHostName('192.168.1.79')
    db.setDatabaseName('tmh_fabrication')
    if db.open():
        return True
    else:
        dbErr(db)
        return False


def dbErr(qry=None):
    """This error is used extensively.
    """
    if qry is None:
        QtGui.QMessageBox.critical(None, "Database Error", "An unknown error occurred")
    else:
        QtGui.QMessageBox.critical(None, "Database Error", qry.lastError().text())
    return
