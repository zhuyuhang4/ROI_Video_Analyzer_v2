"""ROI视频分析工具 v2.0 — Catppuccin Mocha 深色主题 QSS 样式表。

定义所有组件的深色主题样式，包括按钮、滑条、标签、进度条等。
"""

# =========================
# Catppuccin Mocha 色板
# =========================
COLORS = {
    "crust":    "#11111b",
    "mantle":   "#181825",
    "base":     "#1e1e2e",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "text":     "#cdd6f4",
    "subtext1": "#bac2de",
    "lavender": "#7f77dd",
    "green":    "#1d9e75",
    "green_light": "#9fe1cb",
    "red":      "#e24b4a",
    "red_light":    "#f09595",
    "amber":    "#ba7517",
    "yellow":   "#e5c890",
    "blue":     "#89b4fa",
}


def build_stylesheet() -> str:
    """构建并返回完整的 Catppuccin Mocha 深色主题 QSS 样式表。

    Returns:
        str: 完整的 QSS 样式表字符串。
    """
    c = COLORS

    qss = f"""

    /* ===== 全局 ===== */
    QWidget {{
        background-color: {c['base']};
        color: {c['text']};
        font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
        font-size: 14px;
    }}

    QMainWindow {{
        background-color: {c['base']};
    }}

    /* ===== 工具栏 ===== */
    QToolBar {{
        background-color: {c['mantle']};
        border: none;
        padding: 4px 8px;
        spacing: 6px;
        min-height: 42px;
        max-height: 42px;
    }}

    QToolBar::separator {{
        width: 1px;
        background-color: {c['surface1']};
        margin: 4px 6px;
    }}

    /* ===== QPushButton 通用 ===== */
    QPushButton {{
        background-color: {c['surface0']};
        color: {c['text']};
        border: 1px solid {c['surface1']};
        border-radius: 6px;
        padding: 6px 14px;
        min-height: 28px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {c['surface1']};
        border-color: {c['surface2']};
    }}

    QPushButton:pressed {{
        background-color: {c['surface2']};
    }}

    QPushButton:disabled {{
        background-color: {c['crust']};
        color: {c['overlay0']};
        border-color: {c['surface0']};
    }}

    /* ===== QPushButton[class="primary"] 紫色主按钮 ===== */
    QPushButton[class="primary"] {{
        background-color: {c['lavender']};
        color: #1e1e2e;
        border: 1px solid {c['lavender']};
        font-weight: 600;
    }}

    QPushButton[class="primary"]:hover {{
        background-color: #9391e6;
        border-color: #9391e6;
    }}

    QPushButton[class="primary"]:pressed {{
        background-color: #6c65c7;
    }}

    QPushButton[class="primary"]:disabled {{
        background-color: {c['surface0']};
        color: {c['overlay0']};
        border-color: {c['surface0']};
    }}

    /* ===== QPushButton[class="success"] 绿色按钮 ===== */
    QPushButton[class="success"] {{
        background-color: {c['green']};
        color: #1e1e2e;
        border: 1px solid {c['green']};
        font-weight: 600;
    }}

    QPushButton[class="success"]:hover {{
        background-color: #23b587;
        border-color: #23b587;
    }}

    QPushButton[class="success"]:pressed {{
        background-color: #178a66;
    }}

    QPushButton[class="success"]:disabled {{
        background-color: {c['surface0']};
        color: {c['overlay0']};
        border-color: {c['surface0']};
    }}

    /* ===== QPushButton[class="danger"] 红色边框按钮 ===== */
    QPushButton[class="danger"] {{
        background-color: transparent;
        color: {c['red']};
        border: 1px solid {c['red']};
        font-weight: 600;
    }}

    QPushButton[class="danger"]:hover {{
        background-color: rgba(226, 75, 74, 0.15);
        border-color: {c['red_light']};
        color: {c['red_light']};
    }}

    QPushButton[class="danger"]:pressed {{
        background-color: rgba(226, 75, 74, 0.25);
    }}

    QPushButton[class="danger"]:disabled {{
        background-color: transparent;
        color: {c['overlay0']};
        border-color: {c['surface0']};
    }}

    /* ===== QPushButton[class="outline"] 边框按钮 ===== */
    QPushButton[class="outline"] {{
        background-color: transparent;
        color: {c['lavender']};
        border: 1px solid {c['lavender']};
        font-weight: 500;
    }}

    QPushButton[class="outline"]:hover {{
        background-color: rgba(127, 119, 221, 0.15);
        border-color: #9391e6;
    }}

    QPushButton[class="outline"]:pressed {{
        background-color: rgba(127, 119, 221, 0.25);
    }}

    QPushButton[class="outline"]:disabled {{
        background-color: transparent;
        color: {c['overlay0']};
        border-color: {c['surface0']};
    }}

    /* ===== QPushButton[class="outline-success"] 绿色边框按钮 ===== */
    QPushButton[class="outline-success"] {{
        background-color: transparent;
        color: {c['green_light']};
        border: 1px solid {c['green']};
        font-weight: 500;
    }}

    QPushButton[class="outline-success"]:hover {{
        background-color: rgba(29, 158, 117, 0.15);
        border-color: {c['green_light']};
    }}

    QPushButton[class="outline-success"]:pressed {{
        background-color: rgba(29, 158, 117, 0.25);
    }}

    QPushButton[class="outline-success"]:disabled {{
        background-color: transparent;
        color: {c['overlay0']};
        border-color: {c['surface0']};
    }}

    /* ===== QPushButton 扁平图标按钮（工具栏播放控制） ===== */
    QPushButton[class="flat"] {{
        background-color: transparent;
        color: {c['text']};
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 6px 10px;
        min-height: 28px;
    }}

    QPushButton[class="flat"]:hover {{
        background-color: {c['surface0']};
        border-color: {c['surface1']};
    }}

    QPushButton[class="flat"]:pressed {{
        background-color: {c['surface1']};
    }}

    QPushButton[class="flat"]:disabled {{
        background-color: transparent;
        color: {c['overlay0']};
        border-color: transparent;
    }}

    /* ===== QLabel ===== */
    QLabel {{
        background-color: transparent;
        color: {c['text']};
        border: none;
        padding: 0px;
    }}

    /* QLabel[class="section-title"] section标题 */
    QLabel[class="section-title"] {{
        color: {c['lavender']};
        font-size: 15px;
        font-weight: 600;
        padding: 8px 0px 4px 0px;
    }}

    /* QLabel[class="stat-card"] 统计卡片 */
    QLabel[class="stat-card"] {{
        background-color: {c['surface0']};
        color: {c['text']};
        border: 1px solid {c['surface1']};
        border-radius: 8px;
        padding: 10px 8px;
        font-size: 12px;
        text-align: center;
    }}

    /* QLabel[class="stat-value"] 统计值 */
    QLabel[class="stat-value"] {{
        background-color: transparent;
        color: {c['yellow']};
        font-size: 24px;
        font-weight: 700;
        padding: 0px;
        border: none;
    }}

    /* QLabel[class="stat-label"] 统计标签 */
    QLabel[class="stat-label"] {{
        background-color: transparent;
        color: {c['overlay0']};
        font-size: 12px;
        font-weight: 400;
        padding: 0px;
        border: none;
    }}

    /* QLabel[class="chip"] 底部状态chip */
    QLabel[class="chip"] {{
        background-color: {c['surface0']};
        color: {c['subtext1']};
        border: 1px solid {c['surface1']};
        border-radius: 10px;
        padding: 4px 11px;
        font-size: 12px;
    }}

    /* QLabel[class="chip-highlight"] 高亮chip */
    QLabel[class="chip-highlight"] {{
        background-color: rgba(127, 119, 221, 0.18);
        color: {c['lavender']};
        border: 1px solid rgba(127, 119, 221, 0.35);
        border-radius: 10px;
        padding: 3px 10px;
        font-size: 11px;
    }}

    /* ===== QSlider ===== */
    QSlider::groove:horizontal {{
        background-color: {c['surface0']};
        height: 6px;
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background-color: {c['lavender']};
        width: 16px;
        height: 16px;
        margin: -5px 0px;
        border-radius: 8px;
    }}

    QSlider::handle:horizontal:hover {{
        background-color: #9391e6;
    }}

    QSlider::sub-page:horizontal {{
        background-color: {c['lavender']};
        border-radius: 3px;
    }}

    QSlider::groove:vertical {{
        background-color: {c['surface0']};
        width: 6px;
        border-radius: 3px;
    }}

    QSlider::handle:vertical {{
        background-color: {c['lavender']};
        width: 16px;
        height: 16px;
        margin: 0px -5px;
        border-radius: 8px;
    }}

    QSlider::handle:vertical:hover {{
        background-color: #9391e6;
    }}

    QSlider::sub-page:vertical {{
        background-color: {c['lavender']};
        border-radius: 3px;
    }}

    /* ===== QProgressBar ===== */
    QProgressBar {{
        background-color: {c['surface0']};
        border: 1px solid {c['surface1']};
        border-radius: 6px;
        height: 20px;
        text-align: center;
        color: {c['text']};
        font-size: 11px;
    }}

    QProgressBar::chunk {{
        background-color: {c['lavender']};
        border-radius: 5px;
    }}

    /* ===== QSpinBox ===== */
    QSpinBox {{
        background-color: {c['surface0']};
        color: {c['text']};
        border: 1px solid {c['surface1']};
        border-radius: 6px;
        padding: 4px 8px;
        min-height: 26px;
    }}

    QSpinBox:hover {{
        border-color: {c['surface2']};
    }}

    QSpinBox:focus {{
        border-color: {c['lavender']};
    }}

    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {c['surface1']};
        border: none;
        width: 20px;
    }}

    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {c['surface2']};
    }}

    /* ===== QLineEdit ===== */
    QLineEdit {{
        background-color: {c['surface0']};
        color: {c['text']};
        border: 1px solid {c['surface1']};
        border-radius: 6px;
        padding: 6px 10px;
        min-height: 26px;
    }}

    QLineEdit:hover {{
        border-color: {c['surface2']};
    }}

    QLineEdit:focus {{
        border-color: {c['lavender']};
    }}

    /* ===== QGroupBox ===== */
    QGroupBox {{
        background-color: {c['mantle']};
        border: 1px solid {c['surface1']};
        border-radius: 8px;
        margin-top: 12px;
        padding: 16px 12px 12px 12px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        padding: 0px 6px;
        color: {c['lavender']};
        font-size: 14px;
    }}

    /* ===== QScrollArea ===== */
    QScrollArea {{
        background-color: {c['mantle']};
        border: none;
    }}

    QScrollArea > QWidget > QWidget {{
        background-color: {c['mantle']};
    }}

    /* ===== QScrollBar ===== */
    QScrollBar:vertical {{
        background-color: {c['mantle']};
        width: 10px;
        border: none;
    }}

    QScrollBar::handle:vertical {{
        background-color: {c['surface1']};
        border-radius: 6px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {c['surface2']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background-color: {c['mantle']};
        height: 10px;
        border: none;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {c['surface1']};
        border-radius: 6px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {c['surface2']};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ===== QSplitter ===== */
    QSplitter::handle {{
        background-color: {c['surface1']};
    }}

    QSplitter::handle:horizontal {{
        width: 2px;
    }}

    QSplitter::handle:vertical {{
        height: 2px;
    }}

    /* ===== QMenuBar ===== */
    QMenuBar {{
        background-color: {c['crust']};
        color: {c['text']};
        border-bottom: 1px solid {c['surface0']};
    }}

    QMenuBar::item:selected {{
        background-color: {c['surface0']};
    }}

    /* ===== QMessageBox ===== */
    QMessageBox {{
        background-color: {c['base']};
    }}

    QMessageBox QLabel {{
        color: {c['text']};
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
    }}

    /* ===== pyqtgraph PlotWidget 覆盖 ===== */
    pyqtgraph {{
        background-color: {c['mantle']};
    }}

    """

    return qss


# =========================
# 便捷常量导出（供其他模块直接 import）
# =========================
CRUST = COLORS["crust"]
MANTLE = COLORS["mantle"]
BASE = COLORS["base"]
SURFACE0 = COLORS["surface0"]
SURFACE1 = COLORS["surface1"]
SURFACE2 = COLORS["surface2"]
OVERLAY0 = COLORS["overlay0"]
TEXT = COLORS["text"]
SUBTEXT1 = COLORS["subtext1"]
LAVENDER = COLORS["lavender"]
LAVENDER_LIGHT = "#9f97e7"
GREEN = COLORS["green"]
GREEN_LIGHT = COLORS["green_light"]
RED = COLORS["red"]
RED_LIGHT = COLORS["red_light"]
AMBER = COLORS["amber"]
YELLOW = COLORS["yellow"]
BLUE = COLORS["blue"]

# 兼容别名：app.py 等模块使用 build_stylesheet() 获取完整QSS
GLOBAL_QSS = build_stylesheet()
