import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import time
from PyQt5.QtSql import *
from re_path import res_path

class addBookDialog(QDialog):
    add_book_success_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(addBookDialog, self).__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("添加资产")

    def setUpUI(self):
        # 书名，书号，作者，分类，添加数量.出版社,出版日期
        # 书籍分类：哲学类、社会科学类、政治类、法律类、军事类、经济类、文化类、教育类、体育类、语言文字类、艺术类、历史类、地理类、天文学类、生物学类、医学卫生类、农业类
        BookCategory = ["哲学", "社会科学", "政治", "法律", "军事", "经济", "文化", "教育", "体育", "语言文字", "艺术", "历史"
            , "地理", "天文学", "生物学", "医学卫生", "农业"]
        self.resize(300, 400)
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Label控件
        self.titlelabel = QLabel("添加资产")
        self.bookNameLabel = QLabel("*品牌:")
        self.bookIdLabel = QLabel("*设备:")
        self.authNameLabel = QLabel("*型号:")
        self.categoryLabel = QLabel("*数量:")
        self.publisherLabel = QLabel("*单位:")
        # self.publishDateLabel = QLabel("添加时间:")
        self.addNumLabel = QLabel("备注:")

        # button控件
        self.addBookButton = QPushButton("添 加")

        # lineEdit控件
        self.bookNameEdit = QLineEdit()
        self.bookIdEdit = QLineEdit()
        self.authNameEdit = QLineEdit()
        self.categoryComboBox = QLineEdit()
        # self.categoryComboBox = QComboBox()
        # self.categoryComboBox.addItems(BookCategory)
        self.publisherEdit = QLineEdit()
        self.publishTime = QDateTimeEdit()
        self.publishTime.setDisplayFormat("yyyy-MM-dd")
        # self.publishDateEdit = QLineEdit()
        self.addNumEdit = QLineEdit()

        self.bookNameEdit.setMaxLength(50)
        self.bookIdEdit.setMaxLength(50)
        self.authNameEdit.setMaxLength(50)
        self.publisherEdit.setMaxLength(50)
        self.addNumEdit.setMaxLength(50)
        # self.addNumEdit.setValidator(QIntValidator())
        self.categoryComboBox.setValidator(QIntValidator())

        # 添加进formlayout
        self.layout.addRow("", self.titlelabel)
        self.layout.addRow(self.bookNameLabel, self.bookNameEdit)
        self.layout.addRow(self.bookIdLabel, self.bookIdEdit)
        self.layout.addRow(self.authNameLabel, self.authNameEdit)
        self.layout.addRow(self.categoryLabel, self.categoryComboBox)
        self.layout.addRow(self.publisherLabel, self.publisherEdit)
        # self.layout.addRow(self.publishDateLabel, self.publishTime)
        self.layout.addRow(self.addNumLabel, self.addNumEdit)
        self.layout.addRow("", self.addBookButton)

        # 设置字体
        font = QFont()
        font.setPixelSize(20)
        self.titlelabel.setFont(font)
        font.setPixelSize(14)
        self.bookNameLabel.setFont(font)
        self.bookIdLabel.setFont(font)
        self.authNameLabel.setFont(font)
        self.categoryLabel.setFont(font)
        self.publisherLabel.setFont(font)
        # self.publishDateLabel.setFont(font)
        self.addNumLabel.setFont(font)

        self.bookNameEdit.setFont(font)
        self.bookIdEdit.setFont(font)
        self.authNameEdit.setFont(font)
        self.publisherEdit.setFont(font)
        self.publishTime.setFont(font)
        # self.categoryComboBox.setFont(font)
        self.addNumEdit.setFont(font)

        # button设置
        font.setPixelSize(16)
        self.addBookButton.setFont(font)
        self.addBookButton.setFixedHeight(32)
        self.addBookButton.setFixedWidth(140)

        # 设置间距
        self.titlelabel.setMargin(8)
        self.layout.setVerticalSpacing(10)

        self.addBookButton.clicked.connect(self.addBookButtonCicked)

    def addBookButtonCicked(self):
        bookName = self.bookNameEdit.text()  # 品牌
        bookId = self.bookIdEdit.text()  # 设备
        authName = self.authNameEdit.text()  # 型号
        # bookCategory = self.categoryComboBox.currentText()  # 数量
        bookCategory = self.categoryComboBox.text()  # 数量
        publisher = self.publisherEdit.text()  # 单位釦
        # publishTime = self.publishTime.text()
        addBookNum = self.addNumEdit.text()  # 备注
        publishTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        updated_time = publishTime
        if (
                bookName == "" or bookId == "" or authName == "" or bookCategory == "" or publisher == "" or publishTime == ""):
            print(QMessageBox.warning(self, "警告", "有字段为空，添加失败", QMessageBox.Yes, QMessageBox.Yes))
            return
        else:
            # addBookNum = int(addBookNum)
            bookCategory = int(bookCategory)
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName('./db/AssetsManagement.db')
            db.open()
            query = QSqlQuery()
            # 如果已存在，则update Book表的现存量，剩余可借量，不存在，则insert Book表，同时insert buyordrop表
            sql = "select id from Assets WHERE brand='%s' and facility='%s' and model='%s'" % (
            bookName, bookId, authName)
            query.exec_(sql)

            if (query.next()):
                # print(query.value(0))
                sql = "UPDATE Assets SET amount=amount+%d WHERE id='%s'" % (
                    bookCategory, query.value(0))
            else:
                sql = "INSERT INTO Assets(brand,facility,model,amount,unit,remark,created_time,updated_time) VALUES ('%s','%s','%s',%d,'%s','%s','%s','%s')" % (
                    bookName, bookId, authName, bookCategory, publisher, addBookNum, publishTime, updated_time)
                # print(bookName, bookId, authName, bookCategory, publisher, addBookNum, str(publishTime), str(updated_time))
            query.exec_(sql)
            db.commit()
            # # 插入droporinsert表
            # timenow = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            # sql = "INSERT INTO buyordrop VALUES ('%s','%s',1,%d)" % (bookId, timenow, addBookNum)
            # query.exec_(sql)
            # db.commit()
            print(QMessageBox.information(self, "提示", "添加资产成功!", QMessageBox.Yes, QMessageBox.Yes))
            self.add_book_success_signal.emit()
            self.close()
            self.clearEdit()
        return

    def clearEdit(self):
        self.bookNameEdit.clear()
        self.bookIdEdit.clear()
        self.authNameEdit.clear()
        self.addNumEdit.clear()
        self.publisherEdit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(res_path("images/zi.ico")))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = addBookDialog()
    mainMindow.show()
    sys.exit(app.exec_())
