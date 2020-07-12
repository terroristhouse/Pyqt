import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
from PyQt5.QtSql import *
import time
from re_path import res_path
class updateBookDialog(QDialog):
    drop_book_successful_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(updateBookDialog, self).__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("更新资产信息")

    def setUpUI(self):
        # 书名，书号，作者，分类，添加数量.出版社,出版日期
        # 书籍分类：哲学类、社会科学类、政治类、法律类、军事类、经济类、文化类、教育类、体育类、语言文字类、艺术类、历史类、地理类、天文学类、生物学类、医学卫生类、农业类
        BookCategory = ["哲学", "社会科学", "政治", "法律", "军事", "经济", "文化", "教育", "体育", "语言文字", "艺术", "历史"
            , "地理", "天文学", "生物学", "医学卫生", "农业"]
        self.resize(300, 400)
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Label控件
        self.titlelabel = QLabel("更新资产信息")
        self.bookNameLabel = QLabel("*序号:")
        self.bookIdLabel = QLabel("*品牌:")
        self.authNameLabel = QLabel("*设备:")
        self.categoryLabel = QLabel("*型号:")
        self.publisherLabel = QLabel("*数量:")
        self.publishDateLabel = QLabel("*单位:")
        self.dropNumLabel = QLabel("备注:")

        # button控件
        self.dropBookButton = QPushButton("确定更新")

        # lineEdit控件
        self.bookNameEdit = QLineEdit()
        self.bookIdEdit = QLineEdit()
        self.authNameEdit = QLineEdit()
        self.categoryComboBox = QLineEdit()
        # self.categoryComboBox = QComboBox()
        # self.categoryComboBox.addItems(BookCategory)
        self.publisherEdit = QLineEdit()
        self.publishTime = QLineEdit()
        # self.publishDateEdit = QLineEdit()
        self.dropNumEdit = QLineEdit()

        self.bookNameEdit.setMaxLength(50)
        self.bookIdEdit.setMaxLength(50)
        self.authNameEdit.setMaxLength(50)
        self.publisherEdit.setMaxLength(50)
        self.dropNumEdit.setMaxLength(50)
        # self.dropNumEdit.setValidator(QIntValidator())

        # 添加进formlayout
        self.layout.addRow("", self.titlelabel)
        self.layout.addRow(self.bookNameLabel, self.bookNameEdit)
        self.layout.addRow(self.bookIdLabel, self.bookIdEdit)
        self.layout.addRow(self.authNameLabel, self.authNameEdit)
        self.layout.addRow(self.categoryLabel, self.categoryComboBox)
        self.layout.addRow(self.publisherLabel, self.publisherEdit)
        self.layout.addRow(self.publishDateLabel, self.publishTime)
        self.layout.addRow(self.dropNumLabel, self.dropNumEdit)
        self.layout.addRow("", self.dropBookButton)

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
        self.publishDateLabel.setFont(font)
        self.dropNumLabel.setFont(font)

        self.bookNameEdit.setFont(font)
        # self.bookNameEdit.setReadOnly(True)
        # self.bookNameEdit.setStyleSheet("background-color:#363636")
        self.bookIdEdit.setFont(font)
        # self.bookIdEdit.setReadOnly(True)
        # self.bookIdEdit.setStyleSheet("background-color:#363636")
        self.authNameEdit.setFont(font)
        # self.authNameEdit.setReadOnly(True)
        # self.authNameEdit.setStyleSheet("background-color:#363636")
        self.publisherEdit.setFont(font)
        # self.publisherEdit.setReadOnly(True)
        # self.publisherEdit.setStyleSheet("background-color:#363636")
        self.publishTime.setFont(font)
        # self.publishTime.setReadOnly(True)
        # self.publishTime.setStyleSheet("background-color:#363636")
        self.categoryComboBox.setFont(font)
        # self.categoryComboBox.setReadOnly(True)
        # self.categoryComboBox.setStyleSheet("background-color:#363636")
        self.dropNumEdit.setFont(font)
        # self.dropNumEdit.setReadOnly(True)
        # self.dropNumEdit.setStyleSheet("background-color:#363636")

        # button设置
        font.setPixelSize(16)
        self.dropBookButton.setFont(font)
        self.dropBookButton.setFixedHeight(32)
        self.dropBookButton.setFixedWidth(140)

        # 设置间距
        self.titlelabel.setMargin(8)
        self.layout.setVerticalSpacing(10)

        self.dropBookButton.clicked.connect(self.dropBookButtonClicked)
        # self.bookIdEdit.textChanged.connect(self.bookIdEditChanged)
        self.bookNameEdit.textChanged.connect(self.bookIdEditChanged)

    def bookIdEditChanged(self):
        bookId = self.bookNameEdit.text()
        # print(bookId)
        if (bookId == ""):
            # print(123456)
            # self.bookNameEdit.clear() # 序号
            self.bookIdEdit.clear()  # 品牌
            self.authNameEdit.clear()  # 设备
            self.categoryComboBox.clear()  # 型号
            self.publisherEdit.clear()  # 数量
            self.publishTime.clear()  # 备注
            self.dropNumEdit.clear()  # 入库时间
            return
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('./db/AssetsManagement.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT * FROM Assets WHERE id=%d" % (int(bookId))
        query.exec_(sql)
        # 查询对应书号，如果存在就更新form
        if (query.next()):
            # print(query.value(1),query.value(2),query.value(3),query.value(4),query.value(6),query.value(7))
            # self.bookNameEdit.setText(query.value(0))
            self.bookIdEdit.setText(query.value(1))
            self.authNameEdit.setText(query.value(2))
            self.categoryComboBox.setText(query.value(3))
            self.publisherEdit.setText(str(query.value(4)))
            self.publishTime.setText(query.value(5))
            self.dropNumEdit.setText(query.value(6))
        return

    def dropBookButtonClicked(self):
        bookId = int(self.bookNameEdit.text())  # 序号
        bookName = self.bookIdEdit.text()  # 品牌
        authName = self.authNameEdit.text()  # 设备
        bookCategory = self.categoryComboBox.text()  # 型号
        publisher = int(self.publisherEdit.text())  # 数量
        publishTime = self.publishTime.text()  # 单位
        dropNum = self.dropNumEdit.text()  # 备注
        updatedTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 获取现在时间
        if (bookName == "" or bookId == "" or authName == "" or bookCategory == "" or publisher == "" or publishTime == ""):
            print(QMessageBox.warning(self, "警告", "有字段为空，更新失败"), QMessageBox.Yes, QMessageBox.Yes)
            return
        # dropNum = int(self.dropNumEdit.text())
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('./db/AssetsManagement.db')
        db.open()
        query = QSqlQuery()
        # sql = "DELETE  FROM Assets WHERE id='%s'" % (bookId)
        # print(bookName,authName,bookCategory,publisher,publishTime,dropNum,updatedTime,bookId)
        sql = "UPDATE Assets SET brand='{}',facility='{}',model='{}',amount='{}',unit='{}',remark='{}',updated_time='{}' WHERE id='{}'".format(bookName,authName,bookCategory,publisher,publishTime,dropNum,updatedTime,bookId)
        query.exec_(sql)
        db.commit()

        print(QMessageBox.information(self, "提示", "更新成功!", QMessageBox.Yes, QMessageBox.Yes))
        self.drop_book_successful_signal.emit()
        self.close()
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(res_path("images/zi.ico")))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = updateBookDialog()
    mainMindow.show()
    sys.exit(app.exec_())
