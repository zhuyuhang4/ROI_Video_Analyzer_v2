"""ROI视频分析工具 v2.0 — 后台导出线程。

保留原版 ffmpegcv 优先 / OpenCV 回退的双引擎逻辑，
支持 ROI 偶数调整、进度报告、停止控制。
"""

import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class ExportWorker(QThread):
    """后台视频处理线程。

    使用 ffmpegcv 优先处理，失败时回退到 OpenCV。
    对每帧 ROI 计算灰度均值，与阈值比较后输出二值结果。

    Signals:
        progress(int, float, int): 当前帧数, 进度百分比, 总帧数。
        finished(list): 完成后的数据列表 [[frame_num, binary_value], ...]。
        error(str): 错误信息。
        warning(str): 警告信息。
        info(str): 信息消息。
    """

    progress = pyqtSignal(int, float, int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    warning = pyqtSignal(str)
    info = pyqtSignal(str)

    def __init__(self, video_path, roi_coords, threshold, parent=None):
        """初始化导出线程。

        Args:
            video_path: 视频文件路径。
            roi_coords: ROI坐标元组 (x, y, w, h)。
            threshold: 灰度阈值（float）。
            parent: 父QObject。
        """
        super().__init__(parent)
        self.video_path = video_path
        self.roi_coords = roi_coords
        self.threshold = threshold
        self._stop_flag = False

    def stop(self):
        """请求停止处理。"""
        self._stop_flag = True

    @staticmethod
    def adjust_to_even(value):
        """将值调整为最近的偶数（向下）。

        Args:
            value: 整数值。

        Returns:
            int: 偶数值。
        """
        if value % 2 == 1:
            return value - 1
        return value

    def adjust_roi_to_even(self, x, y, w, h):
        """调整ROI坐标为偶数，确保w和h为偶数。

        Args:
            x: ROI左上角x。
            y: ROI左上角y。
            w: ROI宽度。
            h: ROI高度。

        Returns:
            tuple: 调整后的 (x_even, y_even, w_even, h_even)。
        """
        x_even = self.adjust_to_even(x)
        y_even = self.adjust_to_even(y)
        w_even = w if w % 2 == 0 else w + 1
        h_even = h if h % 2 == 0 else h + 1

        if x != x_even or y != y_even or w != w_even or h != h_even:
            self.info.emit(
                f"ROI从 ({x}, {y}, {w}, {h}) 调整为 "
                f"({x_even}, {y_even}, {w_even}, {h_even})"
            )

        return x_even, y_even, w_even, h_even

    def run(self):
        """线程主函数：执行视频处理。"""
        try:
            data = []

            # 方法1：先尝试ffmpegcv
            try:
                import ffmpegcv  # noqa: F401
                self.info.emit("尝试使用ffmpegcv...")
                data = self._process_with_ffmpegcv(data)
            except ImportError:
                self.warning.emit("ffmpegcv未安装，使用OpenCV")
                data = self._process_with_opencv(data)
            except Exception as e:
                self.warning.emit(f"ffmpegcv处理失败: {str(e)}，回退到OpenCV")
                data = self._process_with_opencv(data)

            # 发送完成信号
            if not self._stop_flag:
                self.finished.emit(data)
            else:
                self.info.emit("处理被用户中断")
                self.finished.emit([])

        except Exception as e:
            error_msg = f"处理过程中出现未预期错误: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit([])

    def _process_with_ffmpegcv(self, data):
        """使用ffmpegcv处理视频。

        Args:
            data: 数据列表。

        Returns:
            list: 处理后的数据列表。
        """
        import ffmpegcv

        x, y, w, h = map(int, self.roi_coords)
        x_even, y_even, w_even, h_even = self.adjust_roi_to_even(x, y, w, h)

        self.info.emit(f"原始ROI: ({x}, {y}, {w}, {h})")
        self.info.emit(f"调整后ROI: ({x_even}, {y_even}, {w_even}, {h_even})")

        if w_even <= 0 or h_even <= 0:
            self.error.emit(f"无效的ROI尺寸: 宽度={w_even}, 高度={h_even}")
            return []

        try:
            cap = ffmpegcv.VideoCapture(
                self.video_path,
                crop_xywh=(x_even, y_even, w_even, h_even),
                pix_fmt='bgr24'
            )

            if not cap.isOpened():
                raise RuntimeError(f"无法打开视频: {self.video_path}")

            # 获取视频信息
            total_frames = getattr(cap, 'count', 0)
            if total_frames <= 0:
                temp_cap = cv2.VideoCapture(self.video_path)
                total_frames = int(temp_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                temp_cap.release()

            actual_width = getattr(cap, 'width', w_even)
            actual_height = getattr(cap, 'height', h_even)

            if actual_width != w_even or actual_height != h_even:
                self.warning.emit(
                    f"警告: ROI尺寸不匹配，"
                    f"期望({w_even}x{h_even})，实际({actual_width}x{actual_height})"
                )

            self.info.emit(
                f"视频总帧数: {total_frames}, ROI尺寸: {actual_width}x{actual_height}"
            )

            frame_num = 0
            processed_frames = 0

            while not self._stop_flag:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame is None:
                    data.append([frame_num, 0])
                else:
                    try:
                        expected_shape = (h_even, w_even, 3)
                        if frame.shape != expected_shape:
                            self.warning.emit(
                                f"帧 {frame_num}: 形状不匹配，"
                                f"期望{expected_shape}，实际{frame.shape}"
                            )
                            if frame.size == h_even * w_even * 3:
                                try:
                                    frame = frame.reshape(h_even, w_even, 3)
                                except Exception:
                                    raise RuntimeError("reshape失败")

                        # 转换为灰度
                        if len(frame.shape) == 3:
                            if frame.shape[2] == 3:
                                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            elif frame.shape[2] == 4:
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            else:
                                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                        elif len(frame.shape) == 2:
                            gray = frame
                        else:
                            raise ValueError(f"未知的帧形状: {frame.shape}")

                        mean_value = gray.mean()
                        binary_value = 1 if mean_value > self.threshold else 0
                        data.append([frame_num, binary_value])
                        processed_frames += 1

                    except Exception as e:
                        raise RuntimeError(f"ffmpegcv帧处理失败: {str(e)}")

                frame_num += 1

                if frame_num % 10 == 0 and total_frames > 0:
                    progress = min(100.0, (frame_num / total_frames) * 100)
                    self.progress.emit(frame_num, progress, total_frames)

            cap.release()
            self.info.emit(f"ffmpegcv处理完成，共处理 {processed_frames} 帧有效数据")
            return data

        except Exception as e:
            raise RuntimeError(f"ffmpegcv处理失败: {str(e)}")

    def _process_with_opencv(self, data):
        """使用OpenCV处理视频。

        Args:
            data: 数据列表。

        Returns:
            list: 处理后的数据列表。
        """
        self.info.emit("使用OpenCV处理视频...")

        x, y, w, h = map(int, self.roi_coords)
        self.info.emit(f"使用原始ROI: ({x}, {y}, {w}, {h})")

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.error.emit(f"无法打开视频: {self.video_path}")
            return []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            self.info.emit("动态计算总帧数...")
            temp_cap = cv2.VideoCapture(self.video_path)
            total_frames = 0
            while True:
                ret, _ = temp_cap.read()
                if not ret:
                    break
                total_frames += 1
            temp_cap.release()

        self.info.emit(f"视频总帧数: {total_frames}")

        frame_num = 0
        processed_frames = 0

        while not self._stop_flag:
            ret, frame = cap.read()
            if not ret:
                break

            if frame is None:
                data.append([frame_num, 0])
            else:
                if (y + h <= frame.shape[0] and
                        x + w <= frame.shape[1] and
                        w > 0 and h > 0):
                    try:
                        roi = frame[y:y + h, x:x + w]
                        if roi.size > 0:
                            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                            mean_value = gray.mean()
                            binary_value = 1 if mean_value > self.threshold else 0
                            data.append([frame_num, binary_value])
                            processed_frames += 1
                        else:
                            data.append([frame_num, 0])
                    except Exception:
                        data.append([frame_num, 0])
                else:
                    data.append([frame_num, 0])

            frame_num += 1

            if frame_num % 10 == 0 and total_frames > 0:
                progress = min(100.0, (frame_num / total_frames) * 100)
                self.progress.emit(frame_num, progress, total_frames)

        cap.release()
        self.info.emit(f"OpenCV处理完成，共处理 {processed_frames} 帧有效数据")
        return data
