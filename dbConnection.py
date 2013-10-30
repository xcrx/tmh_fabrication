from PyQt4 import QtCore, QtGui, QtSql


def default_connection():
    QtSql.QSqlDatabase.database('qt_sql_default_connection').close()
    QtSql.QSqlDatabase.removeDatabase('qt_sql_default_connection')
    db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
    db.setUserName('rhanson')
    password, ok = QtGui.QInputDialog.getText(None, 'Enter Password', 'Password', 2)
    if ok:
        db.setPassword(password)
        db.setHostName('192.168.1.79')
        db.setDatabaseName('tmh_fabrication')
        if db.open():
            return True
        else:
            db_err(db)
            return False
    else:
        return False


def db_err(qry=None):
    """This error is used extensively.
    """
    if qry is None:
        QtGui.QMessageBox.critical(None, "Database Error", "An unknown error occurred")
    else:
        QtGui.QMessageBox.critical(None, "Database Error", qry.lastError().text())
    return
