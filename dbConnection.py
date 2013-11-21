from PyQt4 import QtGui, QtSql
import sys
import function
#TODO: Check need for idle check


def default_connection():
    db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
    user = function.TMHSettings().read("user", None, "default_connection").toString()
    if user == "":
        user = get_username()
    db.setUserName(user)
    password, ok = QtGui.QInputDialog.getText(None, 'Enter Password', '%s - Password' % user, 2)
    if ok:
        db.setPassword(password)
        host = function.TMHSettings().read("host", None, "default_connection").toString()
        if host == "":
            host = get_host()
        db.setHostName(host)
        database = function.TMHSettings().read("database", None, "default_connection").toString()
        if database == "":
            database = get_database()
        db.setDatabaseName(database)
        if db.open():
            return True
        else:
            db_err(db)
            return False
    else:
        return False


def clear_connections():
    for con in QtSql.QSqlDatabase.connectionNames():
        db = QtSql.QSqlDatabase.database(con)
        db.close()
        QtSql.QSqlDatabase.removeDatabase(con)
        del db


def db_err(qry=None):
    """
    This error is used extensively.
    """
    if qry is None:
        QtGui.QMessageBox.critical(None, "Database Error", "An unknown error occurred")
    else:
        QtGui.QMessageBox.critical(None, "Database Error", qry.lastError().text())
    return


def get_username():
    user, ok = QtGui.QInputDialog.getText(None, "Username", "Username")
    if ok:
        function.TMHSettings().write("user", user, "default_connection")
        return user
    else:
        sys.exit(1)


def get_host():
    host, ok = QtGui.QInputDialog.getText(None, "Hostname/IP", "Hostname/IP")
    if ok:
        function.TMHSettings().write("host", host, "default_connection")
        return host
    else:
        sys.exit(1)


def get_database():
    database, ok = QtGui.QInputDialog.getText(None, "Database", "Database")
    if ok:
        function.TMHSettings().write("database", database, "default_connection")
        return database
    else:
        sys.exit(1)
