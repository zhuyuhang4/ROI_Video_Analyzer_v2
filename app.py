# -*- coding: utf-8 -*-
"""主窗口 - ROI视频分析工具 v2.0"""

import csv
import os

import cv2
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QSlider, QLabel, QFileDialog, QMessageBox,
    QToolBar, QFrame,
)

from styles import (
    GLOBAL_QSS, MANTLE, SURFACE0, SURFACE1, OVERLAY0, TEXT,
    LAVENDER, GREEN, RED, CRUST,
    COLORS,
)
from video_label import VideoLabel
from side_panel import SidePanel
from export_worker import ExportWorker


class VideoPlayer(QWidget):
    """ROI视频分析工具主窗口。

    布局：工具栏 | QSplitter(视频面板+侧栏)
    视频面板：视频区+状态栏+帧滑条+平移控制+图表
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI 视频分析工具 v2.0")
        self.resize(2500, 1200)
        self.setStyleSheet(GLOBAL_QSS)

        # 视频状态
        self.cap = None
        self.total_frames = 0
        self.cur_frame = 0
        self.video_path = ""

        # 计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)

        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self._plot_next_frame)

        # 导出状态
        self.export_threshold = 128.0
        self.export_col1_name = "Frame"
        self.export_col2_name = "Binary"
        self.export_data = []
        self.export_worker = None
        self.is_processing = False
        self.current_export_id = 0

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- 工具栏 ----
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFixedHeight(42)

        self.btn_open = QPushButton("打开视频")
        self.btn_open.setProperty("class", "primary")
        self.btn_open.setCursor(Qt.PointingHandCursor)

        self.btn_play = QPushButton("▶ 播放")
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_pause = QPushButton("❚❚ 暂停")
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_prev = QPushButton("◀ 上一帧")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_next = QPushButton("下一帧 ▶")
        self.btn_next.setCursor(Qt.PointingHandCursor)

        self.btn_calc = QPushButton("计算均值曲线")
        self.btn_calc.setProperty("class", "success")
        self.btn_calc.setCursor(Qt.PointingHandCursor)

        self.btn_stop = QPushButton("■ 停止")
        self.btn_stop.setProperty("class", "danger")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(False)

        toolbar.addWidget(self.btn_open)
        toolbar.addSeparator()
        toolbar.addWidget(self.btn_play)
        toolbar.addWidget(self.btn_pause)
        toolbar.addWidget(self.btn_prev)
        toolbar.addWidget(self.btn_next)
        toolbar.addSeparator()
        toolbar.addWidget(self.btn_calc)
        toolbar.addWidget(self.btn_stop)

        main_layout.addWidget(toolbar)

        # ---- 主区域 QSplitter ----
        splitter = QSplitter(Qt.Horizontal)

        # == 左侧：视频面板 ==
        video_panel = QWidget()
        video_layout = QVBoxLayout(video_panel)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(0)

        # 视频区 + 垂直平移条
        video_row = QHBoxLayout()
        video_row.setSpacing(0)

        self.video = VideoLabel()
        video_row.addWidget(self.video, 1)

        self.pan_v = QSlider(Qt.Vertical)
        self.pan_v.setEnabled(False)
        self.pan_v.setRange(0, 0)
        self.pan_v.setValue(0)
        self.pan_v.setFixedWidth(20)
        video_row.addWidget(self.pan_v, 0)

        video_layout.addLayout(video_row, 5)

        # 状态栏 chip 条
        stats_bar = QHBoxLayout()
        stats_bar.setSpacing(6)
        stats_bar.setContentsMargins(8, 4, 8, 4)

        self.chip_status = QLabel("● 就绪")
        self.chip_status.setStyleSheet(
            f"background-color: {SURFACE0}; color: {TEXT}; "
            f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
        )

        self.chip_frames = QLabel("总帧数: --")
        self.chip_frames.setStyleSheet(
            f"background-color: {SURFACE0}; color: {TEXT}; "
            f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
        )

        self.chip_roi = QLabel("ROI: 未设置")
        self.chip_roi.setStyleSheet(
            f"background-color: {SURFACE0}; color: {TEXT}; "
            f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
        )

        self.chip_engine = QLabel("引擎: --")
        self.chip_engine.setStyleSheet(
            f"background-color: {SURFACE0}; color: {TEXT}; "
            f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
        )

        self.chip_gray = QLabel("灰度: --")
        self.chip_gray.setStyleSheet(
            f"background-color: {SURFACE0}; color: {TEXT}; "
            f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
        )

        for chip in (self.chip_status, self.chip_frames,
                     self.chip_roi, self.chip_engine, self.chip_gray):
            stats_bar.addWidget(chip)

        stats_bar.addStretch(1)
        video_layout.addLayout(stats_bar, 0)

        # 帧位置滑条
        seek_row = QHBoxLayout()
        seek_row.setSpacing(8)
        seek_row.setContentsMargins(8, 4, 8, 4)

        self.lbl_frame_pos = QLabel("帧位置  -- / --")
        self.lbl_frame_pos.setStyleSheet(
            f"color: {OVERLAY0}; font-size: 13px;"
        )

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self._seek_frame)

        seek_row.addWidget(self.lbl_frame_pos, 0)
        seek_row.addWidget(self.slider, 1)
        video_layout.addLayout(seek_row, 0)

        # 水平平移条
        pan_h_row = QHBoxLayout()
        pan_h_row.setSpacing(8)
        pan_h_row.setContentsMargins(8, 2, 8, 4)

        self.pan_h = QSlider(Qt.Horizontal)
        self.pan_h.setEnabled(False)
        self.pan_h.setRange(0, 0)
        self.pan_h.setValue(0)
        self.pan_h.setFixedHeight(16)

        pan_label = QLabel("平移")
        pan_label.setStyleSheet(f"color: {OVERLAY0}; font-size: 13px;")

        pan_h_row.addWidget(pan_label, 0)
        pan_h_row.addWidget(self.pan_h, 1)
        video_layout.addLayout(pan_h_row, 0)

        # 图表区
        self.plot_widget = pg.PlotWidget(title="ROI灰度均值曲线")
        self.plot_widget.setBackground(QColor(CRUST))
        self.plot_widget.setLabel("left", "灰度均值")
        self.plot_widget.setLabel("bottom", "帧数")
        self.plot_curve = self.plot_widget.plot(pen=pg.mkPen(color=LAVENDER, width=1.5))
        self.plot_widget.setFixedHeight(400)

        video_layout.addWidget(self.plot_widget, 0)

        # == 右侧：侧栏 ==
        self.side_panel = SidePanel()

        # == 组装 QSplitter ==
        splitter.addWidget(video_panel)
        splitter.addWidget(self.side_panel)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([1000, 320])

        main_layout.addWidget(splitter, 1)

    def _connect_signals(self):
        """连接所有信号/槽"""
        # 工具栏按钮
        self.btn_open.clicked.connect(self._open_video)
        self.btn_play.clicked.connect(self._play)
        self.btn_pause.clicked.connect(self._pause)
        self.btn_prev.clicked.connect(self._prev_frame)
        self.btn_next.clicked.connect(self._next_frame_manual)
        self.btn_calc.clicked.connect(self._start_plot)
        self.btn_stop.clicked.connect(self._stop_processing)

        # 侧栏按钮
        self.side_panel.exportCsvRequested.connect(self._threshold_export)
        self.side_panel.calcCurveRequested.connect(self._start_plot)
        self.side_panel.exportPngRequested.connect(self._export_gray_png)
        self.side_panel.stopRequested.connect(self._stop_processing)

        # 阈值变化
        self.side_panel.threshold_widget.thresholdChanged.connect(
            self._on_threshold_changed
        )
        self.side_panel.threshold_widget.colNamesChanged.connect(
            self._on_col_names_changed
        )

        # 视频组件
        self.video.panRangeChanged.connect(self._update_pan_sliders)
        self.video.roiGrayStatsChanged.connect(self._on_roi_stats)

        # 平移滑条
        self.pan_h.valueChanged.connect(lambda v: self.video.set_pan(pan_x=v))
        self.pan_v.valueChanged.connect(lambda v: self.video.set_pan(pan_y=v))

        # 图表数据
        self.plot_x = []
        self.plot_y = []

    # ---- 视频操作 ----

    def _open_video(self):
        """打开视频文件"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.mpg *.mpeg);;所有文件 (*.*)"
        )
        if not path:
            return

        try:
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                QMessageBox.warning(self, "错误", "无法打开视频文件")
                return

            self.video_path = path
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setMaximum(max(0, self.total_frames - 1))

            self.cur_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret:
                self.video.set_frame(frame)
                self.video.reset_pan()
                self._update_status_chips(loaded=path)
                self._update_roi_chip()
                self.setWindowTitle(f"ROI 视频分析工具 v2.0 - {os.path.basename(path)}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开视频失败: {e}")

    def _play(self):
        if self.cap:
            self.timer.start(30)
            self.chip_status.setText("● 播放中")
            self.chip_status.setStyleSheet(
                f"background-color: {SURFACE0}; color: {GREEN}; "
                f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
            )

    def _pause(self):
        self.timer.stop()
        self.plot_timer.stop()
        self.chip_status.setText("● 已暂停")
        self.chip_status.setStyleSheet(
            f"background-color: {SURFACE0}; color: {TEXT}; "
            f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
        )

    def _next_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.chip_status.setText("● 播放完成")
            return

        self.cur_frame += 1
        self.slider.setValue(self.cur_frame)
        self.video.set_frame(frame)
        self._update_frame_pos_label()
        self._update_roi_stats_live()

    def _prev_frame(self):
        if self.cur_frame > 0:
            self.cur_frame -= 1
            self._seek_frame(self.cur_frame)

    def _next_frame_manual(self):
        self._pause()
        self._next_frame()

    def _seek_frame(self, idx):
        if not self.cap:
            return
        self.cur_frame = idx
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = self.cap.read()
        if ret:
            self.video.set_frame(frame)
            self.chip_status.setText(f"● 帧: {idx}")
            self._update_frame_pos_label()
            self._update_roi_stats_live()

    # ---- 图表操作 ----

    def _start_plot(self):
        """开始计算灰度均值曲线"""
        if self.cap is None or self.video.roi is None:
            QMessageBox.warning(self, "警告", "请先打开视频并设置ROI区域")
            return

        self._pause()
        self.plot_x.clear()
        self.plot_y.clear()
        self.plot_curve.setData([], [])

        self.cur_frame = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.plot_timer.start(10)
        self.chip_status.setText("● 生成曲线...")

    def _plot_next_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.plot_timer.stop()
            self.chip_status.setText("● 曲线完成")
            return

        self.video.set_frame(frame)
        stats = self.video.roi_gray_stats()
        if stats:
            mean_val, _, _ = stats
            self.plot_x.append(self.cur_frame)
            self.plot_y.append(mean_val)
            self.plot_curve.setData(self.plot_x, self.plot_y)

        self.cur_frame += 1
        self.slider.setValue(self.cur_frame)

    # ---- 阈值导出 ----

    def _threshold_export(self):
        """阈值处理并导出CSV"""
        if not self.video_path:
            QMessageBox.warning(self, "警告", "请先打开视频")
            return

        if self.video.roi is None:
            QMessageBox.warning(self, "警告", "请先设置ROI区域")
            return

        if self.is_processing:
            reply = QMessageBox.question(
                self, "处理中",
                "已有处理任务在进行中，是否停止并重新开始？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return
            self._stop_processing()

        self._pause()

        self.export_threshold = self.side_panel.threshold_widget.get_threshold()
        col1, col2 = self.side_panel.threshold_widget.get_col_names()
        self.export_col1_name = col1
        self.export_col2_name = col2

        self.current_export_id += 1
        current_id = self.current_export_id

        self.is_processing = True
        self.side_panel.set_processing(True)
        self.btn_stop.setEnabled(True)
        self.btn_calc.setEnabled(False)
        self.btn_open.setEnabled(False)

        self.chip_status.setText("● 处理中...")
        self.chip_engine.setText("引擎: 准备中")

        self.export_data = []

        self.export_worker = ExportWorker(
            self.video_path, self.video.roi, self.export_threshold
        )

        self.export_worker.progress.connect(
            lambda f, p, t: self._on_export_progress(f, p, t, current_id)
        )
        self.export_worker.finished.connect(
            lambda d: self._on_export_finished(d, current_id)
        )
        self.export_worker.error.connect(
            lambda e: self._on_export_error(e, current_id)
        )
        self.export_worker.warning.connect(
            lambda w: self._on_export_warning(w, current_id)
        )
        self.export_worker.info.connect(
            lambda i: self._on_export_info(i, current_id)
        )

        self.export_worker.start()

    def _on_export_progress(self, frame_num, progress, total_frames, export_id):
        if export_id == self.current_export_id:
            self.side_panel.update_progress(frame_num, progress, total_frames)
            self.slider.setValue(min(frame_num, self.total_frames - 1))

    def _on_export_finished(self, data, export_id):
        if export_id != self.current_export_id:
            return

        self._reset_processing_state()
        self.export_data = data

        if data and len(data) > 0:
            self.chip_status.setText("● 处理完成")
            self.side_panel.set_progress_complete(f"完成，共 {len(data)} 帧数据")
            self._save_csv_data()
        else:
            self.chip_status.setText("● 无有效数据")
            self.side_panel.set_progress_complete("无有效数据")
            QMessageBox.warning(
                self, "处理结果",
                "处理完成但未生成有效数据\n\n可能原因：\n"
                "1. ROI区域超出视频范围\n2. 视频格式不支持\n3. 处理被中断"
            )

    def _on_export_error(self, error_msg, export_id):
        if export_id != self.current_export_id:
            return

        self._reset_processing_state()
        self.chip_status.setText("● 处理错误")
        self.side_panel.set_progress_complete("处理错误")
        QMessageBox.critical(self, "处理错误", error_msg)

    def _on_export_warning(self, warning_msg, export_id):
        if export_id == self.current_export_id:
            pass  # 可选：显示警告

    def _on_export_info(self, info_msg, export_id):
        if export_id != self.current_export_id:
            return

        if "ffmpegcv" in info_msg:
            self.chip_engine.setText("引擎: ffmpegcv")
        elif "OpenCV" in info_msg:
            self.chip_engine.setText("引擎: OpenCV")

    def _stop_processing(self):
        """停止当前处理"""
        if self.export_worker and self.export_worker.isRunning():
            self.export_worker.stop()
            self.export_worker.wait(1000)

        self._reset_processing_state()
        self.chip_status.setText("● 已停止")
        self.side_panel.set_progress_complete("已停止")

    def _reset_processing_state(self):
        """重置处理状态"""
        self.is_processing = False
        self.side_panel.set_processing(False)
        self.btn_stop.setEnabled(False)
        self.btn_calc.setEnabled(True)
        self.btn_open.setEnabled(True)

    def _save_csv_data(self):
        """保存CSV数据"""
        if not self.export_data:
            QMessageBox.warning(self, "警告", "没有数据需要保存")
            return

        try:
            default_dir = os.path.dirname(self.video_path)
            default_path = os.path.join(default_dir, "lighting_frame.csv")

            filename, _ = QFileDialog.getSaveFileName(
                self, "保存CSV文件", default_path,
                "CSV文件 (*.csv);;所有文件 (*.*)"
            )

            if not filename:
                self.chip_status.setText("● 已取消保存")
                return

            if not filename.endswith(".csv"):
                filename += ".csv"

            with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([self.export_col1_name, self.export_col2_name])
                writer.writerows(self.export_data)

            self.chip_status.setText(f"● 已保存 {len(self.export_data)} 帧")

            QMessageBox.information(
                self, "处理完成",
                f"成功处理 {len(self.export_data)} 帧数据\n\n"
                f"阈值: {self.export_threshold}\n"
                f"文件: {os.path.basename(filename)}"
            )

        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存CSV文件失败:\n{e}")

    # ---- PNG 导出 ----

    def _export_gray_png(self):
        """使用ffmpegcv提取ROI灰度均值，绘图保存为PNG"""
        if not self.video_path:
            QMessageBox.warning(self, "警告", "请先打开视频")
            return
        if self.video.roi is None:
            QMessageBox.warning(self, "警告", "请先设置ROI区域")
            return

        from matplotlib import pyplot as plt

        self._pause()

        x, y, w, h = map(int, self.video.roi)
        x_even = x if x % 2 == 0 else x - 1
        y_even = y if y % 2 == 0 else y - 1
        w_even = w if w % 2 == 0 else w + 1
        h_even = h if h % 2 == 0 else h + 1

        try:
            import ffmpegcv
            cap = ffmpegcv.VideoCapture(
                self.video_path,
                crop_xywh=(x_even, y_even, w_even, h_even),
                pix_fmt="bgr24",
            )
            if not cap.isOpened():
                raise RuntimeError("无法打开视频")

            gray_means = []
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_means.append(gray.mean())

            cap.release()

            if not gray_means:
                QMessageBox.warning(self, "结果为空", "无法生成灰度图像")
                return

            filename, _ = QFileDialog.getSaveFileName(
                self, "保存灰度图像PNG", "roi_gray_plot.png",
                "PNG 图像 (*.png);;所有文件 (*.*)"
            )
            if not filename:
                return
            if not filename.lower().endswith(".png"):
                filename += ".png"

            plt.figure(figsize=(12, 4))
            plt.plot(gray_means, color="black")
            plt.xlabel("Frame")
            plt.ylabel("Mean Gray Value")
            plt.title("ROI Grayscale Mean Over Time")
            plt.tight_layout()
            plt.savefig(filename, dpi=300)
            plt.close()

            self.chip_status.setText("● 灰度图已保存")
            self.chip_engine.setText("引擎: 灰度图导出")

            QMessageBox.information(self, "完成", f"已保存灰度图到:\n{filename}")
        except ImportError:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise RuntimeError("无法打开视频")
            gray_means = []

            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break
                # 裁剪 ROI
                frame = frame[
                    y_even:y_even + h_even,
                    x_even:x_even + w_even
                ]
                # 转灰度
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # 灰度均值
                gray_means.append(gray.mean())
            cap.release()            
            if not gray_means:
                QMessageBox.warning(self, "结果为空", "无法生成灰度图像")
                return

            filename, _ = QFileDialog.getSaveFileName(
                self, "保存灰度图像PNG", "roi_gray_plot.png",
                "PNG 图像 (*.png);;所有文件 (*.*)"
            )
            if not filename:
                return
            if not filename.lower().endswith(".png"):
                filename += ".png"

            plt.figure(figsize=(12, 4))
            plt.plot(gray_means, color="black")
            plt.xlabel("Frame")
            plt.ylabel("Mean Gray Value")
            plt.title("ROI Grayscale Mean Over Time")
            plt.tight_layout()
            plt.savefig(filename, dpi=300)
            plt.close()

            self.chip_status.setText("● 灰度图已保存")
            self.chip_engine.setText("引擎: 灰度图导出")

            QMessageBox.information(self, "完成", f"已保存灰度图到:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败:\n{e}")

    # ---- UI 更新 ----

    def _update_status_chips(self, loaded=None):
        """更新状态栏chip"""
        if loaded:
            self.chip_status.setText("● 就绪")
            self.chip_status.setStyleSheet(
                f"background-color: {SURFACE0}; color: {GREEN}; "
                f"border-radius: 4px; padding: 3px 8px; font-size: 13px;"
            )
            self.chip_frames.setText(f"总帧数: {self.total_frames}")
            self.chip_engine.setText("引擎: 等待选择")
            self.chip_gray.setText("灰度: --")

    def _update_roi_chip(self):
        """更新ROI状态chip"""
        if self.video.roi:
            x, y, w, h = map(int, self.video.roi)
            self.chip_roi.setText(f"ROI: ({x}, {y}, {w}, {h})")
        else:
            self.chip_roi.setText("ROI: 未设置")

    def _update_frame_pos_label(self):
        """更新帧位置标签"""
        self.lbl_frame_pos.setText(
            f"帧位置  {self.cur_frame} / {self.total_frames}"
        )

    def _update_roi_stats_live(self):
        """实时更新ROI统计"""
        stats = self.video.roi_gray_stats()
        if stats:
            mean_val, min_val, max_val = stats
            threshold = self.side_panel.threshold_widget.get_threshold()
            self.side_panel.update_roi_stats(mean_val, min_val, max_val, threshold)
            self.chip_gray.setText(f"灰度: {mean_val:.1f}")

        self._update_roi_chip()

    def _on_roi_stats(self, mean_val, min_val, max_val):
        """ROI灰度统计变化回调"""
        threshold = self.side_panel.threshold_widget.get_threshold()
        self.side_panel.update_roi_stats(mean_val, min_val, max_val, threshold)
        self.chip_gray.setText(f"灰度: {mean_val:.1f}")
        self._update_roi_chip()

    def _on_threshold_changed(self, value):
        """阈值变化回调"""
        self.export_threshold = float(value)
        # 重新计算二值结果
        stats = self.video.roi_gray_stats()
        if stats:
            mean_val, min_val, max_val = stats
            self.side_panel.update_roi_stats(mean_val, min_val, max_val, value)

    def _on_col_names_changed(self, col1, col2):
        """列名变化回调"""
        self.export_col1_name = col1
        self.export_col2_name = col2

    def _update_pan_sliders(self, x_min, x_max, y_min, y_max):
        """更新平移滑条范围"""
        self.pan_h.blockSignals(True)
        self.pan_h.setMinimum(x_min)
        self.pan_h.setMaximum(x_max)
        self.pan_h.setEnabled(x_min != x_max)
        self.pan_h.setValue(max(x_min, min(self.pan_h.value(), x_max)))
        self.pan_h.blockSignals(False)

        self.pan_v.blockSignals(True)
        self.pan_v.setMinimum(y_min)
        self.pan_v.setMaximum(y_max)
        self.pan_v.setEnabled(y_min != y_max)
        self.pan_v.setValue(max(y_min, min(self.pan_v.value(), y_max)))
        self.pan_v.blockSignals(False)

    # ---- 关闭事件 ----

    def closeEvent(self, event):
        if self.export_worker and self.export_worker.isRunning():
            self.export_worker.stop()
            self.export_worker.wait(3000)

        if self.cap:
            self.cap.release()

        event.accept()
