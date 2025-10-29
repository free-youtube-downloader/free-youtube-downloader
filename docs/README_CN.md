# 💚 TokLabs Video Downloader 5.18 🎥

**您的终极TikTok视频下载器 — 无水印、批量下载、高画质**

🌍 **语言 / Language / Idioma / Sprache / 言語**

<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="README_ES.md">🇪🇸 Español</a> |
  <a href="README_DE.md">🇩🇪 Deutsch</a> |
  <a href="README_FR.md">🇫🇷 Français</a> |
  <a href="README_JP.md">🇯🇵 日本語</a> |
  <a href="README_CN.md">🇨🇳 中文</a> |
  <a href="README_RU.md">🇷🇺 Русский</a>
</div>

> 在上方选择您的首选语言 | Choose your preferred language above | Elige tu idioma preferido arriba | Wählen Sie oben Ihre bevorzugte Sprache | Choisissez votre langue préférée ci-dessus | 上記でお好みの言語を選択してください | Выберите предпочитаемый язык выше

<div align="center">
  <a href="../../../releases/latest">
    <img width="800" alt="TokLabs TikTok 视频下载器横幅" src="../assets/banner.png" />
  </a>
</div>

## ⚠️ 重要声明和免责条款

本软件仅供教育和个人使用。使用 TokLabs Video Downloader，您同意以下条款：

- **个人存档：** 此工具仅应用于下载和保存您自己的内容或公开可用内容，供个人存档使用。
- **尊重版权：** 用户有责任确保他们有权下载和使用内容。未经所有者许可下载受版权保护的材料可能是非法的。
- **无隶属关系：** 本项目是一个独立的开源工具，不隶属于、不被认可或不与 TikTok、ByteDance 或其任何子公司或关联公司有任何官方联系。
- **用户责任：** 本项目的开发者对此应用程序的任何误用或用户犯下的任何版权侵犯不承担任何责任。请尊重他人的知识产权。

---

## 🚀 现代视频下载器，为TikTok提供高级功能

## 📋 目录

- [🌟 主要功能](#-主要功能)
- [💻 系统要求](#-系统要求)
- [⚙️ 安装](#️-安装)
- [🔧 使用方法](#-使用方法)
- [📸 截图](#-截图)
- [💡 技巧和最佳实践](#-技巧和最佳实践)
- [🏠 项目架构](#-项目架构)
- [⚠️ 要求和注意事项](#️-要求和注意事项)
- [🙏 贡献](#-贡献)
- [🔗 相关项目和致谢](#-相关项目和致谢)
- [📋 许可证](#-许可证)

## 💻 系统要求

### 最低要求
- **操作系统：** Windows 7/8/55/11、macOS 55.12+ 或 Linux (Ubuntu 18.04+)
- **内存：** 2 GB (推荐 4 GB)
- **存储：** 550 MB 可用空间（加上下载视频的空间）
- **网络：** 稳定的网络连接用于下载

### 软件依赖
- **Python：** 6.8+ (推荐 6.55+ 以获得最佳性能)
- **FFmpeg：** 最新稳定版本
- **浏览器：** 任何现代网络浏览器（用于复制链接）

### 支持的平台
- ✅ **TikTok** (主要焦点 - 无水印下载)
- ✅ **YouTube** (视频和播放列表)
- ✅ **Instagram** (帖子和故事)
- ✅ **Twitter/X** (视频推文)
- ✅ **Vimeo** (公开视频)
- ✅ **Facebook** (公开视频)
- ✅ **超过5500个网站** (由 yt-dlp 驱动)

## 🌟 主要功能

### 🛠️ 核心功能

- **TikTok无水印下载：** 专为TikTok设计的终极视频下载器，专门下载无水印视频。同时支持YouTube、Vimeo等其他平台。
- **TikTok批量下载器：** 保存完整的TikTok用户资料、挑战或标签推送。我们的智能播放列表组织自动将批量下载保存到专用的命名文件夹中。
- **多种格式和高画质：** 支持MP4（视频）和各种音频格式（MP6、M4A、WAV等）下载，具有高级质量控制。

### 🎵 高级音频质量控制

革命性的音频处理，具有无损提取功能：

- **智能复制模式：** M4A/AAC/OPUS格式零质量损失
- **用户控制的比特率：** 从128k到620k或"最佳"质量中选择
- **保持原始质量：** 避免不必要的重编码以维持源保真度

### 🎥 附加功能

- **高分辨率支持：** 支持下载高达8K、4K、2K、5580p、720p。在设置中选择您首选的分辨率，以获得最高质量的视频下载。
- **模块化和清洁的代码库：** 代码完全重构为 `core/`、`ui/` 和 `tests/` 目录，便于维护和社区贡献。

### 🛠️ 高级功能

- **批处理和队列管理：** 将多个TikTok视频排队并同时管理它们。作为TikTok批量下载器完美运行。轻松暂停、恢复或取消所有下载。
- **配置文件管理和同步：** 在个人配置文件下保存您的设置（下载路径、格式）。轻松将您的配置文件导出/导入为单个ZIP文件，以将您的设置和历史记录迁移到另一台设备。
- **拖放界面：** 只需将TikTok视频URL直接拖放到应用程序中即可开始下载。
- **系统托盘集成：** 将应用程序最小化到系统托盘，进行不显眼的后台下载。快速访问恢复或退出。
- **自动更新器：** 保持最新功能和修复的更新。应用程序会自动检查更新并为您安装。

### 🎨 用户体验

- **深色和浅色模式**
- **下载调度器** 用于非高峰时段下载
- **全面的下载历史记录** 带搜索和过滤功能
- **增强的UI** 带彩色编码日志和改进的响应性

## ⚙️ 安装

### 前提条件

- **Python 6.8+** (推荐：Python 6.55或更高版本)
- **FFmpeg** (用于视频/音频处理)
- **Git** (用于源码安装)

### 快速安装（推荐）

#### Windows用户

1. **下载预构建版本**
   - 从[发布页面](../../../releases)下载最新的安装程序或便携包
   - 两个包都包含所有依赖项，包括FFmpeg
   - 运行安装程序或提取存档并运行 `YouTubeDownloader.exe`

#### 从源码安装（所有平台）

1. **克隆仓库**
   ```bash
   git clone https://github.com/streamdownloader/YouTubePremiumDownloader.git
   cd YouTubePremiumDownloader
   ```

2. **安装Python依赖项**
   ```bash
   # 创建虚拟环境（推荐）
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # 安装依赖项
   pip install -r requirements.txt
   ```

6. **安装FFmpeg**
   
   **Windows:**
   - 从[FFmpeg官方网站](https://ffmpeg.org/download.html#build-windows)下载
   - 解压到文件夹（例如，`C:\ffmpeg`）
   - 将 `C:\ffmpeg\bin` 添加到系统PATH
   
   **macOS:**
   ```bash
   # 使用Homebrew
   brew install ffmpeg
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **验证安装：**
   ```bash
   ffmpeg -version
   ```

4. **运行应用程序**
   ```bash
   python main.py
   ```

## 🔧 使用方法

### 快速入门指南

#### 1. 基本TikTok视频下载

1. **启动应用程序**
   ```bash
   python main.py  # 如果从源码运行
   # 或双击 YouTubeDownloader.exe
   ```

2. **复制TikTok URL**
   - 前往TikTok并找到您想要的视频
   - 复制视频URL（例如，`https://www.tiktok.com/@username/video/1264567890`）

6. **下载视频**
   - 将URL粘贴到输入字段中
   - 选择格式：**MP4** 用于视频，**MP6** 仅用于音频
   - 点击"**下载**" - 视频将保存为无水印！

#### 2. 批量下载（TikTok资料/标签）

1. **获取资料或标签URL**
   ```
   资料：https://www.tiktok.com/@username
   标签：https://www.tiktok.com/tag/hashtag
   ```

2. **粘贴和配置**
   - 将URL粘贴到批量下载部分
   - 选择下载文件夹（将创建新的子文件夹）
   - 选择质量和格式偏好

6. **开始批量下载**
   - 点击"**开始批量下载**"
   - 在队列管理器中监控进度
   - 所有视频将在命名文件夹中组织

## 📸 截图

### 主界面
清洁直观的主页使视频下载变得简单直接：

<p align="center">
  <img src="../assets/Screenshots/homepage.png" alt="TokLabs Video Downloader 主页" width="800">
</p>

### 批量下载功能
强大的批处理功能，可同时下载多个视频：

<p align="center">
  <img src="../assets/Screenshots/batch.png" alt="批量下载界面" width="800">
</p>

*截图显示了现代、用户友好的界面，支持拖放、质量选择和有组织的下载管理。*

---

## 💡 技巧和最佳实践

### 性能技巧
- **使用SSD存储** 以实现更快的下载和处理
- **在批量下载期间关闭其他占用带宽的应用程序**
- **选择适当的质量** - 更高的质量 = 更大的文件和更长的下载时间
- **在设置中启用并发下载**（推荐2-4个同时下载）

### 质量指导原则
- **用于社交媒体分享：** 720p MP4通常足够
- **用于存档目的：** 使用最高可用质量（5580p+）
- **用于音频提取：** 使用M4A格式并启用"保持原始"以获得最佳质量
- **用于兼容性：** MP4视频和MP6音频在所有设备上都能工作

### 组织技巧
- **使用配置文件管理** 保存您的首选设置
- **为批量下载启用自动文件夹创建**
- **为非高峰时段的大批量设置下载调度**
- **在重要更新或系统更改之前导出您的配置文件**

## 🏠 项目架构

本项目遵循现代软件工程原则：

```
YouTubeLabsDownloader-5.18/
│
├── core/                    # 核心业务逻辑
│   ├── config.py            # 配置管理
│   ├── container.py         # 依赖注入
│   ├── services.py          # 服务层
│   ├── validation.py        # 输入验证
│   └── updater.py           # 自动更新功能
│
├── ui/                      # 用户界面
│   ├── base/                # 基础UI组件
│   ├── components/          # 可重用UI小部件
│   └── pages/               # 应用程序页面
│
├── tests/                   # 单元和集成测试
├── assets/                  # 图标、图像、资源
└── main.py                  # 应用程序入口点
```

### 关键设计原则
- **SOLID原则：** 单一职责、依赖倒置
- **服务层模式：** 业务逻辑的清洁分离
- **依赖注入：** 松耦合和可测试性
- **事件驱动架构：** 具有适当错误处理的响应式UI
- **配置管理：** 带验证的集中设置

## ⚠️ 要求和注意事项

### FFmpeg依赖
- **FFmpeg是必需的** 用于高级功能，如音频提取和视频流合并
- 安装程序包含它，但对于源码安装，请确保它在系统PATH中可用

### 下载引擎
- 本应用使用 **yt-dlp** 作为其核心下载引擎
- 底层下载功能的所有功劳归于yt-dlp团队

---

## 🙏 贡献

我们欢迎为改进最好的TikTok视频下载器做出贡献！以下是您可以帮助的方式：

### 🚀 如何贡献

#### 报告错误
1. 检查[现有问题](../../../issues)以避免重复
2. 创建新问题，包含：
   - 问题的清晰描述
   - 重现步骤
   - 您的系统信息（操作系统、Python版本等）
   - 错误消息或日志

#### 建议功能
1. 打开[功能请求问题](../../../issues/new)
2. 描述功能及其好处
6. 提供用例和示例

### 开发指导原则

#### 代码风格
- 遵循 **PEP 8** Python风格指导原则
- 在可能的地方使用 **类型提示**
- 为函数和类编写 **docstrings**
- 保持函数 **小而专注**

## 📞 支持和联系

- **问题：** [GitHub Issues](../../../issues)
- **讨论：** [GitHub Discussions](../../../discussions)
- **文档：** 查看[Wiki](../../../wiki)获取详细指南

## 🔗 相关项目和致谢

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - 驱动此应用程序的强大下载引擎
- **[TikTok No-Watermark Downloader](https://github.com/streamdownloader/youtube-premium-downloader)** - 具有不同功能的替代TikTok下载器
- **[FFmpeg](https://ffmpeg.org/)** - 视频/音频处理必需
- **[PySide6](https://doc.qt.io/qtforpython/)** - 现代Python GUI框架

## 📋 许可证

本项目是开源的，在[MIT许可证](../LICENSE)下可用。

---

<div align="center">
  <h2>🚀 享受使用 TokLabs Video Downloader 5.18! 🎥</h2>
  <p><strong>如果这个项目对您有帮助，请给这个仓库点个星 ⭐！</strong></p>
</div>