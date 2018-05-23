# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings-db.ui'
#
# Created: Fri May 18 08:07:40 2018
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class DbTable(QTableWidget):
	def __init__(self,parent=None):
		super(type(self), self).__init__(parent)
                self.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.verticalHeader().setVisible(False)

		self.connect(self, SIGNAL("cellDoubleClicked(int,int)"), self.notify)


	def notify(self,row,col):
		curr=self.item(row,0);
		pid=int(curr.userdata.get('Pid'))
		cpid=int(curr.userdata.get('Cpid'))
		mtime=float(curr.userdata.get('Boot'))
		self.emit(SIGNAL("recordClicked(int,float)"), pid, mtime)
		self.emit(SIGNAL("childClicked(int,float)"), cpid, mtime)

	def clear(self):
		for col in range(self.columnCount()):
			self.removeColumn(0)
		for row in range(self.rowCount()):
			self.removeRow(0)
		super(type(self),self).clear()

	def show(self, cursor):
		fields=[x[0] for x in cursor.description]
		self.clear()
		self.setSortingEnabled(False)
		for col,f in enumerate(fields):
			item=QTableWidgetItem(f)
			self.insertColumn(col)
			self.setHorizontalHeaderItem(col, item)
		for row, data in enumerate(cursor):
			self.insertRow(row)
			userdata=dict(zip(fields,data))
			for col,f in enumerate(data):
				item=QTableWidgetItem(str(f))
				if col==0:
					item.userdata=userdata
				self.setItem(row,col,item)
		cursor.close()
		
                self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
                self.horizontalHeader().setStretchLastSection(True)
		self.sortItems(0)
		self.setSortingEnabled(True)
		super(QTableWidget,self).show()
	
			
if __name__ == "__main__":
	import sys
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = QtGui.QApplication(sys.argv)
	db=Database()
	db.connect()	
	table=DbTable()
	table.show(db.execute("select * from args limit 5"))
	sys.exit(app.exec_())

