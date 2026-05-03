#!/usr/bin/env python3

import os
import sys
import threading
import queue
import customtkinter as ctk
from tkinter import filedialog


class Transcribe:

    def __init__(self, checkpoint=None, bpm=120):
        self.checkpoint = checkpoint
        self.transcriptor = None
        self.bpm = bpm  # 0=自动检测，>0=手动指定
        self.queue = queue.Queue()
        threading.Thread(target=self.worker, daemon=True).start()

    def hr(self):
        print('─' * 70)

    def enqueue(self, files):
        for file in files:
            print(f'已加入队列: {file}')
            self.queue.put(file)

    def worker(self):
        import torch
        from piano_transcription_inference import PianoTranscription
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.hr()
        print("正在加载 AI 模型与设备，请稍候...")
        self.transcriptor = PianoTranscription(device=device, checkpoint_path=self.checkpoint)

        while True:
            file = self.queue.get()
            try:
                self.inference(file)
            except Exception:
                from traceback import print_exc
                print_exc()
            self.queue.task_done()
            if self.queue.empty():
                self.hr()
                print("队列已全部处理完毕，等待新任务。")
                self.hr()

    def inference(self, file):
        from piano_transcription_inference import sample_rate, load_audio
        from time import time

        self.hr()
        print(f'正在转录: {file}')

        audio_path = file
        output_midi_path = f'{file}.mid'

        # 加载音频
        (audio, _) = load_audio(audio_path, sr=sample_rate, mono=True)

        # BPM：设为0则自动检测
        bpm = self.bpm
        print(f'使用手动 BPM: {bpm}')

        # 转录并输出 MIDI 文件
        transcribe_time = time()
        transcribed_dict = self.transcriptor.transcribe(audio, output_midi_path, bpm=bpm)
        print(f'转录耗时: {time() - transcribe_time:.3f} 秒')
        print(f'已输出 MIDI: {output_midi_path}')


class RedirectText:
    """用于将控制台输出线程安全地重定向到 UI 文本框"""

    def __init__(self, text_ctrl):
        self.text_ctrl = text_ctrl

    def write(self, string):
        # 使用 after 方法确保在主 UI 线程中更新，防止多线程崩溃
        self.text_ctrl.after(0, self._write, string)

    def _write(self, string):
        self.text_ctrl.insert('end', string)
        self.text_ctrl.see('end')

    def flush(self):
        pass


class Gui:

    def __init__(self, transcribe, files=None):
        from platform import system

        self.transcribe = transcribe
        self.ctrl = '⌘' if system() == 'Darwin' else 'Ctrl'

        # --- 核心修改：UI 颜色与字体配置 ---
        # 设置为浅色主题
        ctk.set_appearance_mode("Light")
        # 使用默认的蓝色高亮（在浅色下视觉清晰）
        ctk.set_default_color_theme("blue")

        # 定义全局统一中文字体 ("Microsoft YaHei" 兼容性最好，macOS 会自动映射)
        self.main_font = ("Microsoft YaHei", 13)
        self.main_font_bold = ("Microsoft YaHei", 13, "bold")

        self.root = ctk.CTk()
        self.root.title('PianoTrans - 钢琴转录工作站')
        self.root.geometry('780x550')
        self.root.minsize(650, 400)

        # 核心布局配置
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # 1. 顶部控制面板
        # 浅色模式下，给一个稍微带有对比度的背景色，使层次分明
        self.control_frame = ctk.CTkFrame(self.root, corner_radius=8, fg_color=("gray95", "gray10"))
        self.control_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.control_frame.grid_columnconfigure(2, weight=1)

        # BPM 标签与输入框 (应用统一中文字体)
        self.bpm_label = ctk.CTkLabel(self.control_frame, text="音频 BPM （默认120）:", font=self.main_font_bold)
        self.bpm_label.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="w")

        self.bpm_entry = ctk.CTkEntry(self.control_frame, width=80, font=self.main_font)
        self.bpm_entry.insert(0, str(int(transcribe.bpm)))
        self.bpm_entry.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="w")

        # 添加文件按钮 (应用统一中文字体)
        self.add_btn = ctk.CTkButton(self.control_frame, text="✚ 添加文件到队列",
                                     command=self.open, width=150, font=self.main_font_bold)
        self.add_btn.grid(row=0, column=3, padx=15, pady=15, sticky="e")

        # 2. 日志输出终端 (应用统一中文字体，放弃纯英文的 Consolas 以防中文变方块)
        self.textbox = ctk.CTkTextbox(self.root, corner_radius=8, font=self.main_font)
        self.textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # 接管输出流
        redir = RedirectText(self.textbox)
        sys.stdout = redir
        sys.stderr = redir

        # 处理初始传入的文件
        if files:
            self.transcribe.enqueue(files)

        print("界面初始化完成。等待导入文件...")

        self.root.mainloop()

    def open(self):
        # 读取用户输入的 BPM
        try:
            self.transcribe.bpm = float(self.bpm_entry.get())
        except ValueError:
            self.transcribe.bpm = 0
            self.bpm_entry.delete(0, 'end')
            self.bpm_entry.insert(0, "0")

        files = filedialog.askopenfilenames(
            title=f'选择音频/视频文件，按住 {self.ctrl} 可多选')
        files = self.root.tk.splitlist(files)
        if files:
            self.transcribe.enqueue(files)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='PianoTrans - 钢琴转录工具')
    parser.add_argument('-c', '--cli', action='store_true', help='禁用 GUI（纯命令行模式）')
    parser.add_argument('--bpm', type=float, default=120,
                        help='指定速度 BPM（默认: 120）')
    parser.add_argument('file', nargs='*', help='要转录的音频文件')
    args = parser.parse_args()

    checkpoint = None
    is_bundle = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    if is_bundle:
        # PyInstaller 打包环境
        script_dir = os.path.dirname(sys.argv[0])
        os.environ['PATH'] += os.pathsep + os.path.abspath(os.path.join(script_dir, 'ffmpeg'))
        checkpoint = os.path.abspath(
            os.path.join(script_dir, 'piano_transcription_inference_data', 'note_F1=0.9677_pedal_F1=0.9186.pth'))

    transcribe = Transcribe(checkpoint=checkpoint, bpm=args.bpm)
    files = args.file

    if (not is_bundle and os.isatty(0) and len(files) > 0) or args.cli:
        transcribe.enqueue(files)
        transcribe.queue.join()
    else:
        try:
            Gui(transcribe, files=files)
        except Exception as e:
            print(f'无法打开 GUI: {e}')
            parser.print_help()


if __name__ == '__main__':
    main()