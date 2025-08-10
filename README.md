# Doro 表情包插件

一个基于 [AstrBot](https://github.com/Astronmancer/astrbot) 的插件，用于获取随机的 Doro 表情包，并带有冷却限制，防止过于频繁调用 API。

## 📦 插件信息

- **名称**: doro
- **描述**: 随机 doro 表情包
- **版本**: 0.0.5

## ✨ 功能说明

本插件注册了一个指令 `/doro`，用于从 [https://www.doro.asia/api/random-sticker](https://www.doro.asia/api/random-sticker) 获取一张随机的 Doro 表情包图片，并发送至聊天中。

> 注意：该指令有 5 秒冷却时间，防止频繁请求 API。

本插件还注册了另一个指令 `/cheshire`，用于从 [https://www.cheshire.asia/api/random-sticker](https://www.cheshire.asia/api/random-sticker) 获取一张随机的 Cheshire 表情包图片，并发送至聊天中。

> 注意：该指令同样有冷却时间（默认与 /doro 相同，具体值取决于配置），防止频繁请求 API。

## 🛠 安装方法

将插件文件放入 AstrBot 插件目录中，AstrBot 会在启动时自动加载。

## 🧪 使用方法

### 指令列表

| 指令 | 描述 |
|------|------|
| `/doro` | 获取一张随机 Doro 表情包 |
| `/cheshire` | 获取一张随机 Cheshire 表情包 |

## 📜 更新日志

### v0.0.5
优化代码结构

### v0.0.4
- 新增 `/cheshire` 指令，用于获取随机 Cheshire 表情包。
- 优化了 API 调用失败时的错误提示信息（当 API 返回 success:false 时不再显示具体 URL）。

### v0.0.3
增加了 httpx 请求的重试机制，失败时会重试最多三次。

### v0.0.2
冷却时间可通过配置自行更改

### v0.0.1
初始版本，实现了 /doro 指令，用于获取随机 Doro 表情包。
引入了冷却时间机制，防止频繁调用。
实现了基础的错误处理。

## 📄 License

AGPL-3.0

---

欢迎提交 Issues 或 PR 来帮助改进本插件。
