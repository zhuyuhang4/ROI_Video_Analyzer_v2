#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ROI视频分析工具 v2.0 - 主程序入口"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from app import VideoPlayer


def main():
    # 高DPI缩放支持
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("ROI视频分析工具 v2.0")
    app.setApplicationDisplayName("ROI 视频分析工具 v2.0")

    win = VideoPlayer()
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
