# -*- coding: utf-8 -*-
"""视频显示组件 - VideoLabel，支持ROI绘制/拖拽/缩放/平移"""

import cv2
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel

from styles import CRUST, RED, LAVENDER


class VideoLabel(QLabel):
    """视频显示区域，支持ROI绘制、拖拽移动、角点调整、缩放、平移。

    Signals:
        panRangeChanged(int, int, int, int): 平移范围变化 (x_min, x_max, y_min, y_max)
        roiGrayStatsChanged(float, float, float): 灰度统计变化 (mean, min, max)
    """

    panRangeChanged = pyqtSignal(int, int, int, int)
    roiGrayStatsChanged = pyqtSignal(float, float, float)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {CRUST};")

        self.frame = None
        self.display_frame = None

        self.base_scale = 1.0
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # 平移
        self.pan_x = 0
        self.pan_y = 0
        self._pan_x_min = 0
        self._pan_x_max = 0
        self._pan_y_min = 0
        self._pan_y_max = 0

        # ROI
        self.roi = None  # (x, y, w, h)
        self.drawing = False
        self.dragging = False
        self.resizing = False
        self.start_x = 0.0
        self.start_y = 0.0

        self.setMouseTracking(True)

    # ---- 公共方法 ----

    def set_pan(self, pan_x=None, pan_y=None):
        """设置平移偏移"""
        if pan_x is not None:
            self.pan_x = int(pan_x)
        if pan_y is not None:
            self.pan_y = int(pan_y)

        self.pan_x = max(self._pan_x_min, min(self.pan_x, self._pan_x_max))
        self.pan_y = max(self._pan_y_min, min(self.pan_y, self._pan_y_max))
        self.update()

    def reset_pan(self):
        """重置平移"""
        self.pan_x = 0
        self.pan_y = 0
        self.update()

    def set_frame(self, frame):
        """设置当前帧"""
        self.frame = frame.copy()
        self.update_display()

    def roi_gray_stats(self):
        """计算ROI区域的灰度统计值。

        Returns:
            tuple or None: (mean, min, max) 或 None
        """
        if self.frame is None or self.roi is None:
            return None

        x, y, w, h = map(int, self.roi)
        if y + h > self.frame.shape[0] or x + w > self.frame.shape[1]:
            return None
        roi = self.frame[y : y + h, x : x + w]
        if roi.size == 0:
            return None

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return gray.mean(), float(gray.min()), float(gray.max())

    # ---- 内部方法 ----

    def update_display(self):
        """更新显示帧"""
        if self.frame is None:
            self.update()
            return

        h, w = self.frame.shape[:2]
        lw, lh = self.width(), self.height()
        if lw <= 0 or lh <= 0:
            return

        self.base_scale = min(lw / w, lh / h)
        scale = self.base_scale * self.zoom

        nw, nh = int(w * scale), int(h * scale)

        base_offset_x = (lw - nw) // 2
        base_offset_y = (lh - nh) // 2

        if nw <= lw:
            draw_x_min = base_offset_x
            draw_x_max = base_offset_x
        else:
            draw_x_min = lw - nw
            draw_x_max = 0

        if nh <= lh:
            draw_y_min = base_offset_y
            draw_y_max = base_offset_y
        else:
            draw_y_min = lh - nh
            draw_y_max = 0

        self._pan_x_min = draw_x_min - base_offset_x
        self._pan_x_max = draw_x_max - base_offset_x
        self._pan_y_min = draw_y_min - base_offset_y
        self._pan_y_max = draw_y_max - base_offset_y

        self.pan_x = max(self._pan_x_min, min(self.pan_x, self._pan_x_max))
        self.pan_y = max(self._pan_y_min, min(self.pan_y, self._pan_y_max))

        self.offset_x = base_offset_x
        self.offset_y = base_offset_y

        rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.display_frame = cv2.resize(rgb, (nw, nh))

        self.panRangeChanged.emit(
            self._pan_x_min, self._pan_x_max,
            self._pan_y_min, self._pan_y_max,
        )

        self.update()

    def resizeEvent(self, event):
        self.update_display()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(CRUST))

        if self.display_frame is None:
            return

        h, w, ch = self.display_frame.shape
        img = QImage(self.display_frame.data, w, h, ch * w, QImage.Format_RGB888)

        draw_x = self.offset_x + self.pan_x
        draw_y = self.offset_y + self.pan_y
        painter.drawImage(draw_x, draw_y, img)

        if self.roi:
            x, y, rw, rh = self.roi
            scale = self.base_scale * self.zoom

            # ROI 边框
            painter.setPen(QPen(QColor(RED), 2))
            painter.drawRect(
                int(x * scale) + draw_x,
                int(y * scale) + draw_y,
                int(rw * scale),
                int(rh * scale),
            )

            # 角点拖拽手柄
            handle_size = 10
            painter.fillRect(
                int((x + rw) * scale) + draw_x - handle_size // 2,
                int((y + rh) * scale) + draw_y - handle_size // 2,
                handle_size,
                handle_size,
                QColor(RED),
            )

            # ROI 坐标标签
            roi_text = f"({int(x)}, {int(y)}, {int(rw)}, {int(rh)})"
            painter.setPen(QPen(QColor(RED)))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            text_x = int(x * scale) + draw_x
            text_y = int(y * scale) + draw_y - 4
            if text_y < 14:
                text_y = int(y * scale) + draw_y + 14
            painter.drawText(text_x, text_y, roi_text)

    # ---- 鼠标事件 ----

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            self.zoom *= 1.1 if delta > 0 else 0.9
            self.zoom = max(0.2, min(self.zoom, 5.0))
            self.update_display()

    def _map_to_image(self, event):
        """将鼠标坐标映射到图像坐标"""
        scale = self.base_scale * self.zoom
        draw_x = self.offset_x + self.pan_x
        draw_y = self.offset_y + self.pan_y
        x = (event.x() - draw_x) / scale
        y = (event.y() - draw_y) / scale
        return x, y

    def mousePressEvent(self, event):
        if self.frame is None:
            return

        x, y = self._map_to_image(event)
        if x < 0 or y < 0:
            return

        if self.roi:
            rx, ry, rw, rh = self.roi
            # 角点拖拽检测
            if abs(x - (rx + rw)) < 10 and abs(y - (ry + rh)) < 10:
                self.resizing = True
                return
            # ROI内部拖拽检测
            if rx < x < rx + rw and ry < y < ry + rh:
                self.dragging = True
                self.start_x, self.start_y = x, y
                return

        # 绘制新ROI
        self.drawing = True
        self.roi = (x, y, 0.0, 0.0)
        self.start_x, self.start_y = x, y

    def mouseMoveEvent(self, event):
        if self.frame is None or self.roi is None:
            return

        x, y = self._map_to_image(event)
        rx, ry, rw, rh = self.roi

        if self.drawing:
            self.roi = (
                min(self.start_x, x),
                min(self.start_y, y),
                abs(x - self.start_x),
                abs(y - self.start_y),
            )
        elif self.dragging:
            self.roi = (rx + x - self.start_x, ry + y - self.start_y, rw, rh)
            self.start_x, self.start_y = x, y
        elif self.resizing:
            new_w = max(10, x - rx)
            new_h = max(10, y - ry)
            self.roi = (rx, ry, new_w, new_h)

        self.update()

    def mouseReleaseEvent(self, event):
        changed = self.drawing or self.dragging or self.resizing
        self.drawing = self.dragging = self.resizing = False

        if changed:
            self._emit_roi_changed()

    def _emit_roi_changed(self):
        """ROI变更时发射统计信号"""
        stats = self.roi_gray_stats()
        if stats:
            mean_val, min_val, max_val = stats
            self.roiGrayStatsChanged.emit(mean_val, min_val, max_val)
