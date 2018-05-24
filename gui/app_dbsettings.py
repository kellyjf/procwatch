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

class CurList(list):
	def __init__(self):
		super(list,self).__init__()

	def addrows(self,cursor):
		for row in cursor:
			self.append(row)

	def describe(self,description):
		if not 'description' in self.__dict__:
			self.description = description
	def close(self):
		pass

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
			debug,_=settings.value("db/debug", 0).toInt()
			self.debugCheck.setCheckState(debug)

		
	def get(self, key):
		ret=self.settings.value("db/{}".format(key)).toString()
		return str(ret)

	def accept(self):
		self.settings.setValue("db/server", self.serverLine.text())
		self.settings.setValue("db/port", self.portLine.text())
		self.settings.setValue("db/database", self.databaseLine.text())
		self.settings.setValue("db/user", self.userLine.text())
		self.settings.setValue("db/password", self.passwordLine.text())
		self.settings.setValue("db/debug", self.debugCheck.checkState())
		super(type(self),self).accept()	

class Database(QObject):
	def __init__(self, parent=None):
		super(type(self),self).__init__()
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

		try:
			self.conn = pg.connect(connstr)
		except Exception as e:
			self.conn=None
			self.dbsettings.show()

		return self.conn

	def close(self):
		self.conn.close()

	def execute(self, sql, values=[]):
		if not self.conn:
			self.connect()
		try:
			curr=self.conn.cursor()
			if self.dbsettings.debugCheck.checkState():
				print "DEBUG",curr.mogrify(sql, values)
			curr.execute(sql, values)
			return curr
		except pg.OperationalError as exc:
			self.close()
			self.connect()
			return self.execute(sql, values)


	def dictlist(self, sql, values=[]):
		curr=self.execute(sql,values)
		if curr.description:
			fields=[x[0] for x in curr.description]
			result=[ dict(zip(fields,x)) for x in curr]
			curr.close()
			return result
		else:
			return None

if __name__ == "__main__":
	import sys
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = QtGui.QApplication(sys.argv)
	db=Database()
	db.connect()	
	sys.exit(app.exec_())

