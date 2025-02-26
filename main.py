import asyncio
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qasync import QEventLoop, asyncSlot

from src.const import BILI_JCT, BUVID3, SESSDATA, set_data
from src.log import log_init
from src.orm import set_cookies


class AsyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 大框
        v_box_layout_main = QVBoxLayout()
        # sessdata 部分
        h_box_layout_1 = QHBoxLayout()
        self.SESSDATA_label = QLabel("SESSDATA：", self)
        self.SESSDATA_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.SESSDATA_label.setMinimumWidth(75)
        self.SESSDATA_line_edit = QPlainTextEdit()
        self.SESSDATA_line_edit.setMaximumHeight(50)
        h_box_layout_1.addWidget(self.SESSDATA_label)
        h_box_layout_1.addWidget(self.SESSDATA_line_edit)
        # BILI_JCT 部分
        h_box_layout_2 = QHBoxLayout()
        self.BILI_JCT_label = QLabel("BILI_JCT：", self)
        self.BILI_JCT_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.BILI_JCT_label.setMinimumWidth(75)
        self.BILI_JCT_line_edit = QPlainTextEdit()
        self.BILI_JCT_line_edit.setMaximumHeight(50)
        h_box_layout_2.addWidget(self.BILI_JCT_label)
        h_box_layout_2.addWidget(self.BILI_JCT_line_edit)
        # BUVID3 部分
        h_box_layout_3 = QHBoxLayout()
        self.BUVID3_label = QLabel("BUVID3：", self)
        self.BUVID3_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.BUVID3_label.setMinimumWidth(75)
        self.BUVID3_line_edit = QPlainTextEdit()
        self.BUVID3_line_edit.setMaximumHeight(50)
        h_box_layout_3.addWidget(self.BUVID3_label)
        h_box_layout_3.addWidget(self.BUVID3_line_edit)

        self.plainTextEdit = QPlainTextEdit()
        self.plainTextEdit.setReadOnly(True)  # 锁定
        log_init(self.plainTextEdit)

        self.plainTextEdit_1 = QPlainTextEdit()
        self.plainTextEdit_1.setMaximumHeight(50)

        h_box_layout_4 = QHBoxLayout()
        self.push_button = QPushButton("连接直播间", self)
        self.push_button_1 = QPushButton("发送弹幕", self)
        self.push_button_1.setEnabled(False)
        h_box_layout_4.addWidget(self.push_button)
        h_box_layout_4.addWidget(self.push_button_1)

        self.label = QLabel(
            "本程序为Github开源项目，完全免费使用！只推荐通过官方渠道获取本程序。任何对原程序进行收费售卖行为均为诈骗，谨防上当受骗！谨慎使用来路不明的非官方发布版本，谨防病毒入侵！",
            self,
        )
        # 设置label居中 文字居中 字体红色 加粗
        self.label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.label.setStyleSheet("color:red;font-weight:bold;")

        v_box_layout_main.addLayout(h_box_layout_1)
        v_box_layout_main.addLayout(h_box_layout_2)
        v_box_layout_main.addLayout(h_box_layout_3)
        v_box_layout_main.addWidget(self.plainTextEdit)
        v_box_layout_main.addWidget(self.plainTextEdit_1)
        v_box_layout_main.addLayout(h_box_layout_4)
        v_box_layout_main.addWidget(self.label)
        self.setLayout(v_box_layout_main)

        self.update_text()

        self.push_button.clicked.connect(self.run)
        self.push_button_1.clicked.connect(self.on_async_button_clicked)

    def update_text(self):
        self.SESSDATA_line_edit.setPlainText(SESSDATA)
        self.BILI_JCT_line_edit.setPlainText(BILI_JCT)
        self.BUVID3_line_edit.setPlainText(BUVID3)

    @asyncSlot()
    async def run(self):
        self.push_button.setEnabled(False)
        _SESSDATA = self.SESSDATA_line_edit.toPlainText()
        _BILI_JCT = self.BILI_JCT_line_edit.toPlainText()
        _BUVID3 = self.BUVID3_line_edit.toPlainText()
        if SESSDATA != _SESSDATA:
            set_cookies("SESSDATA", _SESSDATA)
            set_data("SESSDATA", _SESSDATA)
        if BILI_JCT != _BILI_JCT:
            set_cookies("BILI_JCT", _BILI_JCT)
            set_data("BILI_JCT", _BILI_JCT)
        if BUVID3 != _BUVID3:
            set_cookies("BUVID3", _BUVID3)
            set_data("BUVID3", _BUVID3)
        from src.bilibili import bilibili_run

        self.sendPoolReturn = bilibili_run()
        self.push_button_1.setEnabled(True)
        self.push_button_1.setShortcut("Ctrl+S")

    @asyncSlot()  # 使用装饰器标记异步槽
    async def on_async_button_clicked(self):
        self.push_button_1.setEnabled(False)
        msg = self.plainTextEdit_1.toPlainText()
        self.plainTextEdit_1.clear()
        await asyncio.create_task(self.sendPoolReturn.add(msg))
        self.push_button_1.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop=loop)
    window = AsyncApp()
    window.resize(960, 540)
    window.setWindowTitle("bilibili live 欢迎姬 plus - by.ziyii")
    # 设置图标
    window.setWindowIcon(QIcon("./ico/favicon.ico"))
    window.show()
    with loop:
        sys.exit(loop.run_forever())
