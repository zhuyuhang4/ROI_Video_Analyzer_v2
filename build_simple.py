#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ROI视频分析工具 v2.0 简化版打包脚本
onefile + windowed 模式
"""

import PyInstaller.__main__
import os
import shutil

ENTRY_SCRIPT = "main.py"
APP_NAME = "ROI_Video_Analyzer_v2"

def main():
    print("开始打包ROI视频分析工具 v2.0（onefile）...")

    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
            print(f"清理文件夹: {folder}")

    args = [
        ENTRY_SCRIPT,
        f"--name={APP_NAME}",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",

        # 收集子模块/数据
        "--collect-submodules=ffmpegcv",
        "--collect-data=ffmpegcv",
        "--collect-submodules=pyqtgraph",
        "--collect-data=pyqtgraph",
        "--collect-submodules=matplotlib",
        "--collect-data=matplotlib",

        # 关键隐藏导入
        "--hidden-import=PyQt5.sip",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=cv2",
        "--hidden-import=cv2.cv2",
        "--hidden-import=numpy",

        # v2.0 新增模块
        "--hidden-import=app",
        "--hidden-import=styles",
        "--hidden-import=video_label",
        "--hidden-import=side_panel",
        "--hidden-import=threshold_widget",
        "--hidden-import=export_worker",

        # 排除不必要模块
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=tkinter",
    ]

    print("运行PyInstaller...")
    PyInstaller.__main__.run(args)

    print("\n" + "=" * 50)
    print("打包完成！")
    print(f"可执行文件位置: dist/{APP_NAME}.exe")
    print("=" * 50)

if __name__ == "__main__":
    main()
