# PianoTrans - 钢琴转录工作站

> ⚠️ **声明**：本项目 fork 自 [azuwis/pianotrans](https://github.com/azuwis/pianotrans)，大部分新增代码由 AI 辅助生成，**未经充分测试，不保证可用性**。使用前请自行评估风险。

基于 [ByteDance 钢琴转录模型](https://github.com/bytedance/piano_transcription) 的 Windows GUI 工具，可将钢琴录音转录为带踏板的 MIDI 文件。

---

## 🆕 本分支改动

| 改动 | 说明 |
|------|------|
| 中文 UI | 基于 customtkinter 重构，全中文化界面 |
| BPM 手动指定 | 默认 120 BPM，解决 MIDI 导入 DAW 后小节线错位问题 |
| RTX 50 系显卡 | 内置 PyTorch 2.11 + CUDA 12.8，支持 5070/5070 Ti/5080/5090 |
| 启动体验 | 不再自动弹出文件选择窗口，改为按钮手动触发 |
| 全量打包 | 开箱即用的 .7z 分发包，无需安装 Python 环境 |

---

## 📦 下载与使用

1. 在 [Releases](../../releases) 页面下载最新 `.7z` 文件
2. 解压到任意目录
3. 双击 `PianoTrans.exe` 启动
4. 输入 BPM（默认 120），点击「添加文件到队列」，选择音频文件
5. 转录完成后 MIDI 文件保存在音频同目录下

### 系统要求

- Windows 10 / 11 64-bit
- NVIDIA 显卡（推荐 RTX 系列，驱动 ≥ R570）
- 至少 8 GB 内存
- 无需安装 Python 或 CUDA Toolkit

---

## 🛠 自行构建

```powershell
# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 2. 安装 PyTorch（CUDA 12.8 版）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128

# 3. 安装依赖
pip install piano_transcription_inference resampy customtkinter

# 4. 下载模型权重
# 放到 %USERPROFILE%\piano_transcription_inference_data\note_F1=0.9677_pedal_F1=0.9186.pth
# 下载地址见原项目 README

# 5. 运行
python PianoTrans.py
```

---

## ⚠️ 已知问题 & 免责声明

- **AI 生成代码**：除原项目代码外，本分支的 UI 重构、BPM 逻辑、打包配置等均由 AI（Claude / DeepSeek）辅助生成，可能包含未发现的 bug
- **未充分测试**：仅在 Windows 11 + RTX 5070 Ti 环境下做过基本功能验证，其他显卡/系统未测试
- **BPM 功能**：自动检测已移除，默认写死 120 BPM。如需其他速度请手动输入
- **不提供技术支持**：如有问题请自行排查或提交 Issue（但可能无人回复）

---

## 🔗 相关项目

| 项目 | 说明 |
|------|------|
| [azuwis/pianotrans](https://github.com/azuwis/pianotrans) | 上游项目（原始 GUI 打包） |
| [bytedance/piano_transcription](https://github.com/bytedance/piano_transcription) | 字节跳动钢琴转录模型（学术研究） |
| [qiuqiangkong/piano_transcription_inference](https://github.com/qiuqiangkong/piano_transcription_inference) | 推理工具包 |

---

## 📄 许可证

本项目基于原项目 [azuwis/pianotrans](https://github.com/azuwis/pianotrans) 修改，沿用其 MIT 许可证。
