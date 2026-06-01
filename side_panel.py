# -*- coding: utf-8 -*-
"""右侧参数侧栏 - ROI统计 + 阈值参数 + 导出操作"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QGroupBox, QScrollArea,
    QFrame,
)

from styles import (
    MANTLE, SURFACE0, SURFACE1, OVERLAY0, TEXT, SUBTEXT1,
    LAVENDER, LAVENDER_LIGHT, GREEN, GREEN_LIGHT, RED,
    GLOBAL_QSS,
)
from threshold_widget import ThresholdWidget


class StatCard(QWidget):
    """统计数值卡片"""

    def __init__(self, label_text, value_text="--", value_color=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "stat-card")
        self.setStyleSheet(f"""
            QWidget[class="stat-card"] {{
                background-color: {SURFACE0};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setStyleSheet(f"color: {OVERLAY0}; font-size: 14px;")

        color = value_color or TEXT
        self.value = QLabel(value_text)
        self.value.setStyleSheet(
            f"color: {color}; font-size: 16px; font-weight: 500;"
        )

        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, text, color=None):
        self.value.setText(text)
        if color:
            self.value.setStyleSheet(
                f"color: {color}; font-size: 16px; font-weight: 500;"
            )


class SidePanel(QWidget):
    """右侧参数侧栏。

    Signals:
        exportCsvRequested(): 请求阈值处理导出CSV
        calcCurveRequested():  请求计算灰度均值曲线
        exportPngRequested(): 请求导出ROI灰度图PNG
        stopRequested():       请求停止处理
    """

    exportCsvRequested = pyqtSignal()
    calcCurveRequested = pyqtSignal()
    exportPngRequested = pyqtSignal()
    stopRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(GLOBAL_QSS)

        # 用 QScrollArea 包裹防止小屏溢出
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background-color: {MANTLE}; border: none;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {MANTLE};")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ---- Section 1: ROI 实时统计 ----
        stats_group = QGroupBox("ROI 实时统计")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(6)

        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(6)

        self.stat_mean = StatCard("灰度均值", "--", LAVENDER_LIGHT)
        self.stat_min = StatCard("最小值", "--")
        self.stat_max = StatCard("最大值", "--")
        self.stat_binary = StatCard("二值结果", "--", GREEN)

        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        left_col.addWidget(self.stat_mean)
        left_col.addWidget(self.stat_max)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.addWidget(self.stat_min)
        right_col.addWidget(self.stat_binary)

        stats_grid.addLayout(left_col)
        stats_grid.addLayout(right_col)
        stats_layout.addLayout(stats_grid)

        main_layout.addWidget(stats_group)

        # ---- Section 2: 阈值参数 ----
        thresh_group = QGroupBox("阈值参数")
        thresh_layout = QVBoxLayout(thresh_group)
        thresh_layout.setSpacing(6)

        self.threshold_widget = ThresholdWidget()
        thresh_layout.addWidget(self.threshold_widget)

        main_layout.addWidget(thresh_group)

        # ---- Section 3: 导出操作 ----
        export_group = QGroupBox("导出操作")
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(6)

        self.btn_export_csv = QPushButton("  阈值处理 → 导出 CSV")
        self.btn_export_csv.setProperty("class", "export-accent")
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)

        self.btn_calc_curve = QPushButton("  计算灰度均值曲线")
        self.btn_calc_curve.setProperty("class", "export-default")
        self.btn_calc_curve.setCursor(Qt.PointingHandCursor)

        self.btn_export_png = QPushButton("  导出 ROI 灰度图 PNG")
        self.btn_export_png.setProperty("class", "export-success")
        self.btn_export_png.setCursor(Qt.PointingHandCursor)

        self.btn_stop = QPushButton("  停止处理")
        self.btn_stop.setProperty("class", "danger")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(False)

        export_layout.addWidget(self.btn_export_csv)
        export_layout.addWidget(self.btn_calc_curve)
        export_layout.addWidget(self.btn_export_png)
        export_layout.addWidget(self.btn_stop)

        # 进度区域
        progress_label = QLabel("处理进度")
        progress_label.setStyleSheet(f"color: {OVERLAY0}; font-size: 14px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)

        self.progress_text = QLabel("等待处理...")
        self.progress_text.setStyleSheet(f"color: {OVERLAY0}; font-size: 14px;")

        export_layout.addWidget(progress_label)
        export_layout.addWidget(self.progress_bar)
        export_layout.addWidget(self.progress_text)

        main_layout.addWidget(export_group)

        main_layout.addStretch(1)

        scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        # 连接信号
        self.btn_export_csv.clicked.connect(self.exportCsvRequested)
        self.btn_calc_curve.clicked.connect(self.calcCurveRequested)
        self.btn_export_png.clicked.connect(self.exportPngRequested)
        self.btn_stop.clicked.connect(self.stopRequested)

    # ---- 公共接口 ----

    def update_roi_stats(self, mean_val, min_val, max_val, threshold):
        """更新ROI统计显示"""
        self.stat_mean.set_value(f"{mean_val:.1f}", LAVENDER_LIGHT)
        self.stat_min.set_value(str(int(min_val)))
        self.stat_max.set_value(str(int(max_val)))

        binary = 1 if mean_val > threshold else 0
        color = GREEN if binary == 1 else RED
        self.stat_binary.set_value(str(binary), color)

    def set_processing(self, is_processing):
        """设置处理中状态"""
        self.btn_export_csv.setEnabled(not is_processing)
        self.btn_calc_curve.setEnabled(not is_processing)
        self.btn_export_png.setEnabled(not is_processing)
        self.btn_stop.setEnabled(is_processing)

        if is_processing:
            self.progress_bar.setValue(0)
            self.progress_text.setText("处理中...")
            self.progress_text.setStyleSheet(f"color: {LAVENDER_LIGHT}; font-size: 14px;")
        else:
            self.progress_text.setStyleSheet(f"color: {OVERLAY0}; font-size: 14px;")

    def update_progress(self, frame_num, progress_pct, total_frames):
        """更新进度"""
        self.progress_bar.setValue(int(progress_pct))
        self.progress_text.setText(
            f"处理中: {frame_num}/{total_frames} 帧 ({progress_pct:.1f}%)"
        )

    def set_progress_complete(self, message):
        """设置处理完成"""
        self.progress_bar.setValue(100)
        self.progress_text.setText(message)
        self.progress_text.setStyleSheet(f"color: {GREEN_LIGHT}; font-size: 14px;")
