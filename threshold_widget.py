# -*- coding: utf-8 -*-
"""阈值参数组件 - 滑条+数字联动，分割预览"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSlider, QSpinBox, QLineEdit, QFrame,
)

from styles import (
    SURFACE0, SURFACE1, OVERLAY0, TEXT, LAVENDER, RED, MANTLE, CRUST,
)


class ThresholdPreviewBar(QWidget):
    """阈值分割预览条，可视化显示暗区(0)/亮区(1)的分割效果。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threshold = 128
        self.setFixedHeight(24)

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = max(0, min(255, int(value)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        # 暗区（0）
        dark_width = int(w * (self._threshold / 255))
        if dark_width > 0:
            painter.fillRect(0, 0, dark_width, h, QColor(SURFACE0))

        # 亮区（1）
        bright_width = w - dark_width
        if bright_width > 0:
            painter.fillRect(dark_width, 0, bright_width, h, QColor(LAVENDER))

        # 分割线
        painter.setPen(QPen(QColor(RED), 2))
        painter.drawLine(dark_width, 0, dark_width, h)

        # 标签
        painter.setPen(QPen(QColor(OVERLAY0)))
        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        if dark_width > 30:
            painter.drawText(4, h // 2 + 4, "0 (暗)")
        if bright_width > 30:
            painter.drawText(dark_width + 4, h // 2 + 4, "1 (亮)")


class ThresholdWidget(QWidget):
    """阈值参数设置组件，包含滑条、数字输入、分割预览、列名输入。

    Signals:
        thresholdChanged(int): 阈值变化
        colNamesChanged(str, str): 列名变化 (col1, col2)
    """

    thresholdChanged = pyqtSignal(int)
    colNamesChanged = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 阈值滑条+数字联动
        thresh_layout = QHBoxLayout()
        thresh_layout.setSpacing(8)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, 255)
        self.spin_box.setValue(128)
        self.spin_box.setFixedWidth(64)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.setValue(128)

        self.spin_box.valueChanged.connect(self._on_spin_changed)
        self.slider.valueChanged.connect(self._on_slider_changed)

        thresh_layout.addWidget(self.spin_box)
        thresh_layout.addWidget(self.slider, 1)
        layout.addLayout(thresh_layout)

        # 分割预览条
        self.preview_bar = ThresholdPreviewBar()
        layout.addWidget(self.preview_bar)

        # 提示文字
        hint = QLabel("高于阈值 → 1，低于 → 0")
        hint.setStyleSheet(f"color: {OVERLAY0}; font-size: 14px;")
        layout.addWidget(hint)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {SURFACE0}; max-height: 1px;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # 列名输入
        col_label = QLabel("CSV 输出列名称")
        col_label.setStyleSheet(f"color: {OVERLAY0}; font-size: 14px;")
        layout.addWidget(col_label)

        col_layout = QHBoxLayout()
        col_layout.setSpacing(6)

        self.col1_input = QLineEdit("Frame")
        self.col1_input.setPlaceholderText("第一列")
        self.col2_input = QLineEdit("Binary")
        self.col2_input.setPlaceholderText("第二列")

        self.col1_input.textChanged.connect(self._on_col_changed)
        self.col2_input.textChanged.connect(self._on_col_changed)

        col_layout.addWidget(self.col1_input)
        col_layout.addWidget(self.col2_input)
        layout.addLayout(col_layout)

    def _on_spin_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.preview_bar.threshold = value
        self.thresholdChanged.emit(value)

    def _on_slider_changed(self, value):
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(value)
        self.spin_box.blockSignals(False)
        self.preview_bar.threshold = value
        self.thresholdChanged.emit(value)

    def _on_col_changed(self):
        self.colNamesChanged.emit(
            self.col1_input.text(),
            self.col2_input.text(),
        )

    # ---- 公共接口 ----

    def get_threshold(self):
        """获取当前阈值"""
        return self.spin_box.value()

    def get_col_names(self):
        """获取列名称 (col1, col2)"""
        col1 = self.col1_input.text() or "Frame"
        col2 = self.col2_input.text() or "Binary"
        return col1, col2
