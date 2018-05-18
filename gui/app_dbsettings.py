# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings-db.ui'
#
# Created: Fri May 18 08:07:40 2018
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from  ui_dbsettings import *
import psycopg2 as pg

class DbSettings(QDialog, Ui_DbSettings):
	def __init__(self,parent=None, settings=None):
		super(QDialog, self).__init__(parent)
		self.setupUi(self)
	
		if settings:
			self.settings=settings
			server=settings.value("db/server", "localhost").toString()
			self.serverLine.setText(server)
			port=settings.value("db/port", "5432").toString()
			self.portLine.setText(port)
			database=settings.value("db/database", "ftrace").toString()
			self.databaseLine.setText(database)
			user=settings.value("db/user", "").toString()
			self.userLine.setText(user)
			password=settings.value("db/password", "").toString()
			self.passwordLine.setText(password)

		
	def accept(self):
		self.settings.setValue("db/server", self.serverLine.text())
		self.settings.setValue("db/port", self.portLine.text())
		self.settings.setValue("db/database", self.databaseLine.text())
		self.settings.setValue("db/user", self.userLine.text())
		self.settings.setValue("db/password", self.passwordLine.text())
		super(type(self),self).accept()	

class Database(QObject):
	def __init__(self, parent=None):
		self.settings=QSettings("Gogo, Inc", "procwatch")
		self.dbsettings=DbSettings(parent, self.settings)
		
	def connect(self):
		connstr=""
		if self.dbsettings.serverLine.text():
			connstr=connstr+" host={}".format(self.dbsettings.serverLine.text())
		if self.dbsettings.portLine.text():
			connstr=connstr+" port={}".format(self.dbsettings.portLine.text())
		if self.dbsettings.databaseLine.text():
			connstr=connstr+" dbname={}".format(self.dbsettings.databaseLine.text())
		if self.dbsettings.userLine.text():
			connstr=connstr+" user={}".format(self.dbsettings.userLine.text())
		if self.dbsettings.passwordLine.text():
			connstr=connstr+" password={}".format(self.dbsettings.passwordLine.text())

		self.conn = pg.connect(connstr)
		return self.conn

	def execute(self, sql, values=[]):
		curr=self.conn.cursor()
		curr.execute(sql, values)
		fields=[x[0] for x in curr.description]
		ret=[dict(zip(fields, x)) for x in curr]
		return ret

if __name__ == "__main__":
	import sys
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = QtGui.QApplication(sys.argv)
	db=Database()
	db.connect()	
	print db.execute("select * from args limit 5")	
	sys.exit(app.exec_())

