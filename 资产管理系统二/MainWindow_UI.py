import sys
import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from re_path import res_path
import qdarkstyle
import sqlite3


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
        self.PageRecordCount = 3

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
        self.search_list = ['按设备查询', '按品牌查询', '按型号查询', '按备注查询','按位置查询']
        self.searchCombo.addItems(self.search_list)
        self.searchCombo.setFixedHeight(32)

        self.topvhbox.addWidget(self.searchEdit)
        self.topvhbox.addWidget(self.searchBtn)
        self.topvhbox.addWidget(self.searchCombo)

        '''中间表格显示部分'''
        self.tableview = QTableView()
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        '''下方分页和查询'''
        self.addBtn = QPushButton('添加资产')
        self.delBtn = QPushButton('删除资产')
        self.updateBtn = QPushButton('修改资产信息')

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
        self.bottomleft.addWidget(self.updateBtn)

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

        # run函数
        self.run()

    # 逻辑
    '''填充数据+翻页+跳转start'''

    def setView(self):
        # model = QStandardItemModel(40, 4)
        # model.setHorizontalHeaderLabels(
        #     ['标题一', '标题二', '标题三', '标题四', '标题五', '标题六', '标题七', '标题八', '标题九', '标题十', '标题十一', '标题十二', '标题十三'])
        # for row in range(40):
        #     for column in range(13):
        #         item = QStandardItem('row %s,column %s' % (row, column))
        #         model.setItem(row, column, item)
        # 声明查询模型
        self.queryModel = QSqlQueryModel(self)

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
        self.tiaoCom.addItems(self.tiao_list)
        # 更新页面
        self.updateStatus()
        # 记录查询
        self.recordQuery(0)
        # 设置模型
        self.tableview.setModel(self.queryModel)
        self.queryModel.setHeaderData(0, Qt.Horizontal, "序号")
        self.queryModel.setHeaderData(1, Qt.Horizontal, "品牌")
        self.queryModel.setHeaderData(2, Qt.Horizontal, "设备")
        self.queryModel.setHeaderData(3, Qt.Horizontal, "型号")
        self.queryModel.setHeaderData(4, Qt.Horizontal, "数量")
        self.queryModel.setHeaderData(5, Qt.Horizontal, "单位")
        self.queryModel.setHeaderData(6, Qt.Horizontal, "位置")
        self.queryModel.setHeaderData(7, Qt.Horizontal, "备注")
        self.queryModel.setHeaderData(8, Qt.Horizontal, "入库时间")
        self.queryModel.setHeaderData(9, Qt.Horizontal, "修改时间")


    # 得到记录数
    def getTotalRecordCount(self):
        self.queryModel.setQuery('select * from Assets')
        rowCount = self.queryModel.rowCount()
        # print('rowCount=' + str(rowCount))
        return rowCount

    # 得到页数
    def getPageCount(self):
        if self.totalRecrodCount % self.PageRecordCount == 0:
            return (self.totalRecrodCount / self.PageRecordCount)
        else:
            return (self.totalRecrodCount / self.PageRecordCount + 1)

    # # 记录查询
    # def recordQuery(self, limitIndex):
    #     szQuery = ('select * from Assets limit %d,%d' % (limitIndex, self.PageRecordCount))
    #     # print('query sql=' + szQuery)
    #     self.queryModel.setQuery(szQuery)
    #     # print(self.queryModel.rowCount())

    # 刷新状态
    def updateStatus(self):
        szCurrentText = ('当前第%d/%d页' % (self.currentPage,self.totalPage))
        self.currentText.setText(szCurrentText)
        # self.page.setText('/%d页' % int(self.totalPage))
        # 设置按钮是否可用
        if self.currentPage == 1 and self.currentPage == int(self.totalPage):
            print(1111)
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

    # # 设置总数页文本
    # def setTotalPageLabel(self):
    #     szPageCountText = ('总共%d页' % self.totalPage)
    #     self.totalPageLabel.setText(szPageCountText)

    # 设置总记录数
    def setTotalRecordLabel(self):
        szTotalRecordText = ('总共%d条记录' % self.totalRecrodCount)
        # print('*** setTotalRecordLabel szTotalRecordText=' + szTotalRecordText)
        self.totalRecord.setText(szTotalRecordText)

    # 前一页按钮按下
    def onPrevButtonClick(self):
        # print('*** onPrevButtonClick')
        limitIndex = (self.currentPage - 2) * self.PageRecordCount
        # print(limitIndex)
        self.recordQuery(limitIndex)
        self.currentPage -= 1
        self.updateStatus()

    # 后一页按钮按下
    def onNextButtonClick(self):
        # print('*** onNextButtonClick')
        limitIndex = self.currentPage * self.PageRecordCount
        # print(limitIndex)
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
        queryCondition = ""
        conditionChoice = self.searchCombo.currentText()
        if (conditionChoice == "按品牌查询"):
            conditionChoice = 'brand'
        elif (conditionChoice == "按设备查询"):
            conditionChoice = 'facility'
        elif (conditionChoice == "按型号查询"):
            conditionChoice = 'model'
        elif (conditionChoice == "按备注查询"):
            conditionChoice = 'remark'
        elif (conditionChoice == '按入库时间查询'):
            conditionChoice = 'created_time'
        elif conditionChoice == '按位置查询':
            conditionChoice = 'location'
        else:
            conditionChoice = 'updated_time'

        if (self.searchEdit.text() == ""):
            queryCondition = 'select * from Assets limit %d,%d' % (index, self.PageRecordCount)
            self.queryModel.setQuery(queryCondition)
            return

        # 得到模糊查询条件
        temp = self.searchEdit.text()
        s = '%'
        for i in range(0, len(temp)):
            s = s + temp[i] + "%"
        # queryCondition = ("SELECT brand,facility,model,amount,unit,remark,created_time,updated_time FROM Assets WHERE %s LIKE '%s' ORDER BY %s " % (conditionChoice, s, conditionChoice))
        queryCondition = ("SELECT * FROM Assets WHERE %s LIKE '%s' ORDER BY %s " % (conditionChoice, s, conditionChoice))
        self.queryModel.setQuery(queryCondition)
        # self.totalRecord = self.queryModel.rowCount()
        # 得到查询的记录数
        self.totalRecrodCount = self.queryModel.rowCount()
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
            print(QMessageBox.information(self, "提醒", "查询无记录", QMessageBox.Yes, QMessageBox.Yes))
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
            queryCondition = ('select * from Assets limit %d,%d' % (index, self.PageRecordCount))
            print(queryCondition)
            self.queryModel.setQuery(queryCondition)
            return
        # 设置分页
        queryCondition = ("SELECT * FROM Assets WHERE %s LIKE '%s' ORDER BY %s LIMIT %d,%d " % (
        conditionChoice, s, conditionChoice, index, self.PageRecordCount))
        self.queryModel.setQuery(queryCondition)
        return

    # 点击查询
    def searchButtonClicked(self):
        self.currentPage = 1
        index = (self.currentPage - 1) * self.PageRecordCount
        print(index)
        self.recordQuery(index)
        return

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
