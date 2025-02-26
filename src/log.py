import logging
import re
import sys

from loguru import logger


class LoguruToQPlainTextEdit:
    def __init__(self, plain_text_edit):
        self.plain_text_edit = plain_text_edit

    def write(self, message):
        # 将 ANSI 颜色代码转换为 HTML
        html_message = self.ansi_to_html(message)
        # 输出到 QPlainTextEdit
        self.plain_text_edit.appendHtml(html_message)

    @staticmethod
    def ansi_to_html(text):
        # ANSI 颜色代码正则表达式
        ansi_regex = re.compile(r"\x1b\[([0-9;]+)m")
        # ANSI 颜色代码到 HTML 的映射
        ansi_to_html_map = {
            # 基础颜色
            "30": "color:black;",
            "31": "color:red;",
            "32": "color:green;",
            "33": "color:yellow;",
            "34": "color:blue;",
            "35": "color:magenta;",
            "36": "color:cyan;",
            "37": "color:white;",
            # 亮色
            "90": "color:gray;",
            "91": "color:lightred;",
            "92": "color:lightgreen;",
            "93": "color:lightyellow;",
            "94": "color:lightblue;",
            "95": "color:lightmagenta;",
            "96": "color:lightcyan;",
            "97": "color:brightwhite;",
            # 背景色
            "40": "background-color:black;",
            "41": "background-color:red;",
            "42": "background-color:green;",
            "43": "background-color:yellow;",
            "44": "background-color:blue;",
            "45": "background-color:magenta;",
            "46": "background-color:cyan;",
            "47": "background-color:white;",
        }

        # 替换 ANSI 代码为 HTML 标签
        def replace_ansi(match):
            codes = match.group(1).split(";")
            styles = []
            for code in codes:
                if code in ansi_to_html_map:
                    styles.append(ansi_to_html_map[code])
            if styles:
                return f'<span style="{" ".join(styles)}">'
            return ""

        # 替换 ANSI 代码并添加换行
        text = ansi_regex.sub(replace_ansi, text)
        text = text.replace("\x1b[0m", "</span>")  # 重置颜色
        return text


def log_init(QtApp):
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=True)
    logger.add(
        "./log/log.log",
        rotation="1 MB",
        retention="10 days",
        compression="zip",
        colorize=True,
    )
    logger.add(LoguruToQPlainTextEdit(QtApp).write, level="INFO", colorize=True)
    _logging = logging.getLogger()
    console_handler = logging.StreamHandler(LoguruToQPlainTextEdit(QtApp))
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    _logging.addHandler(console_handler)
