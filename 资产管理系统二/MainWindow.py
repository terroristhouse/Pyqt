import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from re_path import res_path
import qdarkstyle
import sqlite3
import csv
from datetime import datetime


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        '''连接数据库'''
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./db/AssetsManagement.db')
        self.db.open()

        # 总数页文本
        self.totalPageLabel = None
        # 当前页文本
        self.currentPageLabel = None
        # 转到页输入框
        # self.switchPageLineEdit = None
        # 当前页
        self.currentPage = 0
        # 总页数
        self.totalPage = 0
        # 总记录数
        self.totalRecrodCount = 0
        # 每页显示记录数
        self.PageRecordCount = 50

        '''界面'''
        self.initUI()

    # 界面
    def initUI(self):
        self.setWindowTitle('欢迎使用资产管理系统')
        self.setWindowIcon(QIcon(res_path('./images/zi.ico')))
        self.resize(900, 600)
        '''头部布局'''
        self.topvhbox = QHBoxLayout()
        '''整体布局'''
        self.mainvbox = QVBoxLayout()
        '''尾部布局'''
        self.bottomhbox = QHBoxLayout()
        self.bottomleft = QHBoxLayout()
        self.bottomright = QHBoxLayout()
        '''设置字体'''
        font = QFont()
        font.setPixelSize(16)
        '''搜索框'''
        self.searchEdit = QLineEdit()
        self.searchEdit.setFixedHeight(32)
        self.searchEdit.setFont(font)
        '''搜索按钮'''
        self.searchBtn = QPushButton('查询')
        self.searchBtn.setFont(font)
        self.searchBtn.setFixedHeight(32)
        self.searchBtn.setIcon(QIcon(QPixmap(res_path('./images/search.png'))))
        '''选择搜索类别'''
        self.searchCombo = QComboBox()
        self.searchCombo.setFont(font)
        self.searchCombo.setFixedHeight(32)
        self.search_list = ['按房间号查询', '按使用部门查询', '按责任人查询', '按资产名称查询', '按规格型号查询', '按涉密级别查询', '按设备编号查询', '按领用时间查询',
                            '按状态查询', '按备注查询']
        self.searchCombo.addItems(self.search_list)
        '''排序框'''
        self.sortCombo = QComboBox()
        self.sortCombo.setFont(font)
        self.sortCombo.setFixedHeight(32)
        self.sort_list = ['默认排序', '按房间号排序', '按使用部门排序', '按责任人排序', '按资产名称排序', '按规格型号排序', '按涉密级别排序', '按设备编号排序', '按领用时间排序',
                          '按状态排序', '按备注排序']
        self.sortCombo.addItems(self.sort_list)

        self.topvhbox.addWidget(self.searchEdit)
        self.topvhbox.addWidget(self.searchBtn)
        self.topvhbox.addWidget(self.searchCombo)
        self.topvhbox.addWidget(self.sortCombo)

        '''中间表格显示部分'''
        self.tableview = QTableView()
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        '''下方分页和查询'''
        self.addBtn = QPushButton('添加资产')
        self.delBtn = QPushButton('删除资产')
        self.updateBtn = QPushButton('修改资产信息')
        self.exprotBtn = QPushButton('导出为csv表格')

        self.currentText = QLabel('当前第x页')

        self.tiaoLabel = QLabel('跳转到第')

        self.tiaoCom = QComboBox()

        self.tiaoLabel_1 = QLabel('页')

        self.tiaoBtn = QPushButton('跳转')
        self.prevBtn = QPushButton('前一页')
        self.nextBtn = QPushButton('后一页')
        self.totalRecord = QLabel('共x条记录')

        self.bottomleft.setAlignment(Qt.AlignLeft)
        self.bottomleft.addWidget(self.addBtn)
        self.bottomleft.addWidget(self.delBtn)
        self.bottomleft.addWidget(self.exprotBtn)
        # self.bottomleft.addWidget(self.updateBtn)

        self.bottomright.setAlignment(Qt.AlignRight)
        self.bottomright.addWidget(self.currentText)
        self.bottomright.addWidget(self.tiaoLabel)
        self.bottomright.addWidget(self.tiaoCom)
        self.bottomright.addWidget(self.tiaoLabel_1)
        self.bottomright.addWidget(self.tiaoBtn)
        self.bottomright.addWidget(self.prevBtn)
        self.bottomright.addWidget(self.nextBtn)
        self.bottomright.addWidget(self.totalRecord)
        self.bottomhbox.addLayout(self.bottomleft)
        self.bottomhbox.addLayout(self.bottomright)

        self.mainvbox.addLayout(self.topvhbox)
        self.mainvbox.addWidget(self.tableview)
        self.mainvbox.addLayout(self.bottomhbox)
        self.setLayout(self.mainvbox)

        # 信号连接
        self.prevBtn.clicked.connect(self.onPrevButtonClick)
        self.nextBtn.clicked.connect(self.onNextButtonClick)
        self.tiaoBtn.clicked.connect(self.onSwitchPageButtonClick)
        self.searchBtn.clicked.connect(self.searchButtonClicked)
        self.addBtn.clicked.connect(self.addrow)
        self.delBtn.clicked.connect(lambda: self.model.removeRow(self.tableview.currentIndex().row()))
        self.exprotBtn.clicked.connect(self.exportButtonClicked)
        # run函数
        self.run()

    # 逻辑
    '''填充数据+翻页+跳转start'''

    def setView(self):
        # 设置显示模型
        self.model = QSqlTableModel(self)
        # 设置数据库
        self.model.setTable('Assets')
        # 设置更新模式-实时更新
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)

        # 设置默认排序方式
        self.orderby = 'id'
        # 设置当前页
        self.currentPage = 1
        # 得到总记录数
        self.totalRecrodCount = self.getTotalRecordCount()
        # 设置总记录数
        self.setTotalRecordLabel()
        # 得到总页数
        self.totalPage = self.getPageCount()
        # 设置页数选项
        self.tiao_list = [str(i + 1) for i in range(int(self.totalPage))]
        self.tiaoCom.clear()
        self.tiaoCom.addItems(self.tiao_list)
        # 更新页面
        self.updateStatus()

        # 记录查询
        self.recordQuery(0)
        # 不显示第0列
        # self.model.removeColumn(0)
        # 设置模型
        self.model.setHeaderData(0, Qt.Horizontal, "序号")
        self.model.setHeaderData(1, Qt.Horizontal, "房间号")
        self.model.setHeaderData(2, Qt.Horizontal, "使用部门")
        self.model.setHeaderData(3, Qt.Horizontal, "责任人")
        self.model.setHeaderData(4, Qt.Horizontal, "资产名称")
        self.model.setHeaderData(5, Qt.Horizontal, "规格型号")
        self.model.setHeaderData(6, Qt.Horizontal, "涉密级别")
        self.model.setHeaderData(7, Qt.Horizontal, "设备编号")
        self.model.setHeaderData(8, Qt.Horizontal, "领用时间")
        self.model.setHeaderData(9, Qt.Horizontal, "状态")
        self.model.setHeaderData(10, Qt.Horizontal, "备注")
        self.tableview.setModel(self.model)
        # self.tableview.setWindowTitle('title')

    # 得到记录数
    def getTotalRecordCount(self):
        self.model.setFilter('')
        self.model.select()
        while self.model.canFetchMore():
            self.model.fetchMore()
        rowCount = self.model.rowCount()
        return rowCount

    # 得到页数
    def getPageCount(self):
        if self.totalRecrodCount % self.PageRecordCount == 0:
            return (self.totalRecrodCount / self.PageRecordCount)
        else:
            return (self.totalRecrodCount / self.PageRecordCount + 1)

    # 刷新状态
    def updateStatus(self):
        szCurrentText = ('当前第%d/%d页' % (self.currentPage, self.totalPage))
        self.currentText.setText(szCurrentText)
        # 设置按钮是否可用
        if self.currentPage == 1 and self.currentPage == int(self.totalPage):
            self.prevBtn.setEnabled(False)
            self.nextBtn.setEnabled(False)
        if self.currentPage == 1:
            self.prevBtn.setEnabled(False)
            self.nextBtn.setEnabled(True)
        elif self.currentPage == int(self.totalPage):
            self.prevBtn.setEnabled(True)
            self.nextBtn.setEnabled(False)
        else:
            self.prevBtn.setEnabled(True)
            self.nextBtn.setEnabled(True)

    # 设置总记录数
    def setTotalRecordLabel(self):
        szTotalRecordText = ('总共%d条记录' % self.totalRecrodCount)
        self.totalRecord.setText(szTotalRecordText)

    # 前一页按钮按下
    def onPrevButtonClick(self):
        limitIndex = (self.currentPage - 2) * self.PageRecordCount
        self.recordQuery(limitIndex)
        self.currentPage -= 1
        self.updateStatus()

    # 后一页按钮按下
    def onNextButtonClick(self):
        limitIndex = self.currentPage * self.PageRecordCount
        self.recordQuery(limitIndex)
        self.currentPage += 1
        self.updateStatus()

    # 转到页按钮按下
    def onSwitchPageButtonClick(self):
        # 得到输入字符串
        szText = self.tiaoCom.currentText()
        # 得到页数
        pageIndex = int(szText)
        limitIndex = (pageIndex - 1) * self.PageRecordCount

        # 记录查询
        self.recordQuery(limitIndex)
        # 设置当前页
        self.currentPage = pageIndex
        # 刷新状态
        self.updateStatus()

    '''填充数据+翻页+跳转end'''
    '''搜索功能start'''

    # 记录查询
    def recordQuery(self, index):
        self.queryCondition = ""
        conditionChoice = self.searchCombo.currentText()
        if (conditionChoice == "按房间号查询"):
            conditionChoice = 'room_number'
        elif (conditionChoice == "按使用部门查询"):
            conditionChoice = 'branch'
        elif (conditionChoice == "按责任人查询"):
            conditionChoice = 'person'
        elif (conditionChoice == "按资产名称查询"):
            conditionChoice = 'asset_name'
        elif (conditionChoice == '按规格型号查询'):
            conditionChoice = 'models'
        elif conditionChoice == '按涉密级别查询':
            conditionChoice = 'rank'
        elif conditionChoice == '按设备编号查询':
            conditionChoice = 'number'
        elif conditionChoice == '按领用时间查询':
            conditionChoice = 'created_time'
        elif conditionChoice == '按状态查询':
            conditionChoice = 'status'
        elif conditionChoice == '按备注查询':
            conditionChoice = 'remark'
        self.orderby = self.sortCombo.currentText()
        if (self.orderby == "按房间号排序"):
            self.orderby = 'room_number'
        elif (self.orderby == "按使用部门排序"):
            self.orderby = 'branch'
        elif (self.orderby == "按责任人排序"):
            self.orderby = 'person'
        elif (self.orderby == "按资产名称排序"):
            self.orderby = 'asset_name'
        elif (self.orderby == '按规格型号排序'):
            self.orderby = 'models'
        elif self.orderby == '按涉密级别排序':
            self.orderby = 'rank'
        elif self.orderby == '按设备编号排序':
            self.orderby = 'number'
        elif self.orderby == '按领用时间排序':
            self.orderby = 'created_time'
        elif self.orderby == '按状态排序':
            self.orderby = 'status'
        elif self.orderby == '按备注排序':
            self.orderby = 'remark'
        else:
            self.orderby = 'id'
        if (self.searchEdit.text() == ""):
            # 得到总记录数
            self.totalRecrodCount = self.getTotalRecordCount()
            # 设置总记录数
            self.setTotalRecordLabel()
            # 得到总页数
            self.totalPage = self.getPageCount()
            # 设置页数选项
            self.tiao_list = [str(i + 1) for i in range(int(self.totalPage))]
            self.tiaoCom.clear()
            self.tiaoCom.addItems(self.tiao_list)
            # 更新页面
            self.updateStatus()
            self.queryCondition = 'id > 0 ORDER BY %s limit %d,%d;' % (self.orderby, index, self.PageRecordCount)
            self.model.setFilter(self.queryCondition)
            self.model.select()
            return

        # 得到模糊查询条件
        temp = self.searchEdit.text()
        s = '%'
        for i in range(0, len(temp)):
            s = s + temp[i] + "%"
        # queryCondition = ("SELECT brand,facility,model,amount,unit,remark,created_time,updated_time FROM Assets WHERE %s LIKE '%s' ORDER BY %s " % (conditionChoice, s, conditionChoice))
        self.queryCondition = ("%s LIKE '%s' ORDER BY %s;" % (conditionChoice, s, self.orderby))
        self.model.setFilter(self.queryCondition)
        self.model.select()
        # 得到查询的记录数
        self.totalRecrodCount = self.model.rowCount()
        # 设置查询记录数
        self.setTotalRecordLabel()
        # 得到查询页数
        self.totalPage = self.getPageCount()
        # 设置页数选项
        self.tiao_list = [str(i + 1) for i in range(int(self.totalPage))]
        self.tiaoCom.clear()
        self.tiaoCom.addItems(self.tiao_list)
        # 更新页面
        self.updateStatus()
        # 当查询无记录时的操作
        if self.totalRecrodCount == 0:
            QMessageBox.information(self, "提醒", "查询无记录", QMessageBox.Yes, QMessageBox.Yes)
            self.searchEdit.clear()
            # 得到总记录数
            self.totalRecrodCount = self.getTotalRecordCount()
            # 设置查询记录数
            self.setTotalRecordLabel()
            # 得到查询页数
            self.totalPage = self.getPageCount()
            # 设置页数选项
            self.tiao_list = [str(i + 1) for i in range(int(self.totalPage))]
            self.tiaoCom.clear()
            self.tiaoCom.addItems(self.tiao_list)
            # 更新页面
            self.updateStatus()
            self.queryCondition = ('1=1 ORDER BY %s limit %d,%d;' % (self.orderby, index, self.PageRecordCount))
            # print(queryCondition)
            self.model.setFilter(self.queryCondition)
            self.model.select()
            return
        self.queryCondition = ("%s LIKE '%s' ORDER BY %s LIMIT %d,%d;" % (
            conditionChoice, s, self.orderby, index, self.PageRecordCount))
        self.model.setFilter(self.queryCondition)
        self.model.select()
        return

    # 点击导出
    def exportButtonClicked(self):
        print(self.queryCondition)
        headers = ['序号', '房间号', '使用部门', '责任人', '资产名称', '规格型号', '涉密级别', '设备编号', '领用时间', '状态', '备注']
        res_name = str(datetime.now().strftime('%Y-%m-%d %H%M%S')) + ' 星期' + str(datetime.now().isoweekday())
        con = sqlite3.connect('./db/AssetsManagement.db')
        cursor = con.cursor()
        search_sql = 'select * from Assets where {}'.format(self.queryCondition)
        cursor.execute(search_sql)
        data = cursor.fetchall()
        data_list = []
        for i, j in zip(range(len(data)), data):
            j = list(j)
            j[0] = i + 1
            data_list.append(j)

        with open('./' + res_name + '.csv', 'w', newline='') as f:
            ff = csv.writer(f)
            ff.writerow(headers)
            ff.writerows(data_list)
        QMessageBox.information(self, '提示', '导出成功', QMessageBox.Yes | QMessageBox.Yes)
        cursor.close()
        con.close()

    # 点击查询
    def searchButtonClicked(self):
        self.currentPage = 1
        index = (self.currentPage - 1) * self.PageRecordCount
        # print(index)
        self.recordQuery(index)
        return

    def addrow(self):
        # QMessageBox.information(self, "提醒", "添加资产时序号不用填写", QMessageBox.Yes, QMessageBox.Yes)
        self.model.insertRows(self.model.rowCount(), 1)

    # 重现关闭按钮功能，关闭数据库
    def closeEvent(self, event):
        self.db.close()

    # 规划函数
    def run(self):
        self.setView()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win.show()
    win.showMaximized()
    sys.exit(app.exec_())
