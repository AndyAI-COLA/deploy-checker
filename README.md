# 🛠️ Deploy Checker — 系统环境检测工具

一个轻量级的命令行工具，一键检查当前系统是否满足部署要求，支持彩色终端输出和 JSON 报告生成。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![CI](https://img.shields.io/github/actions/workflow/status/AndyAI-COLA/deploy-checker/test.yml?branch=main&label=CI)

---

## ✨ 功能亮点

- 🔍 **6 大检查项**：Python / Node.js / Git / 网络 / 端口 / 磁盘
- 🎨 **彩色终端输出**：绿色=通过，红色=未通过，一目了然
- ⚡ **耗时显示**：每项检查精确到毫秒
- 📄 **双格式报告**：同时生成 `.log` 文本日志和 `.json` 结构化报告
- 🔧 **灵活过滤**：`--check-only` 只跑你关心的检查项
- 📦 **零依赖**：纯 Python 标准库，无需 `pip install`

---

## 📸 效果预览

> 将终端截图放入 `screenshots/` 目录后取消下方注释即可显示

<!-- ![终端效果](screenshots/terminal.png) -->

```
============================================================
  SYSTEM ENVIRONMENT CHECK
  2026-09-16 15:01:57
============================================================

[1/6] Python version ...
  [PASS] Python 3.14.7        Version 3.14.7, OK             (0ms)

[2/6] Node.js ............
  [PASS] v24.19.0             v24.19.0                       (42ms)

[3/6] Git .................
  [PASS] git version 2.55.0   git version 2.55.0.windows.5   (49ms)

[4/6] Network ............
  [PASS] Reachable            Ping 8.8.8.8 OK                (1095ms)

[5/6] Ports ..............
  [PASS] Available    Port 8080 is available         (2003ms)
  [PASS] Available    Port 3000 is available         (2002ms)
  [PASS] Available    Port 5000 is available         (2011ms)

[6/6] Disk space .........
  [PASS] Free 74.9GB / Total 371.0GB  Usage 79.8%, Free 74.9GB OK  (7ms)

============================================================
  SUMMARY
============================================================

  Total checks: 8
  Passed: 8
  Failed: 0
  Score: [####################] 100%

  >> ALL CHECKS PASSED - System is ready for deployment!
============================================================
```

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/AndyAI-COLA/deploy-checker.git
cd deploy-checker
```

### 2. 运行全部检查
```bash
python checker.py
```

### 3. 只检查指定项目
```bash
python checker.py -c python git disk
```

### 4. 自定义输出文件名
```bash
python checker.py -o my_report
```

### 5. 组合使用
```bash
python checker.py -c python node -o env_check
```

---

## 📋 检查项目说明

| 检查项 | key | 说明 | 判定条件 |
|--------|-----|------|----------|
| Python | `python` | 检查版本 | ≥ 3.8 为通过 |
| Node.js | `node` | 检查是否安装 | 能输出版本号即通过 |
| Git | `git` | 检查是否安装 | 能输出版本号即通过 |
| Network | `network` | Ping 8.8.8.8 | 能连通即通过 |
| Ports | `ports` | 检查 8080/3000/5000 | 端口空闲为通过 |
| Disk | `disk` | 检查磁盘剩余空间 | > 5GB 为通过 |

---

## 📂 输出文件

### JSON 报告结构
```json
{
  "title": "System Check Report",
  "time": "2026-09-16 15:01:57",
  "system": { "os": "Windows", "python": "3.14.7" },
  "summary": { "total": 8, "passed": 8, "failed": 0 },
  "results": [
    {
      "name": "Python",
      "passed": true,
      "detail": "Python 3.14.7",
      "duration_ms": 0
    }
  ]
}
```

---

## 📁 项目结构

```
deploy-checker/
├── checker.py              # 主程序（唯一核心文件）
├── requirements.txt        # 依赖声明（无第三方依赖）
├── README.md               # 项目说明
├── CONTRIBUTING.md         # 贡献指南
├── LICENSE                 # MIT 开源协议
├── .gitignore              # Git 忽略规则
└── .github/
    └── workflows/
        └── test.yml        # GitHub Actions 自动化测试
```

---

## 🛠️ 自定义扩展

如果需要新增检查项，在 `checker.py` 中：

1. 编写检查函数，返回标准格式的 dict：
```python
def check_my_item():
    # 你的检查逻辑
    ok = True  # 或 False
    return dict(
        name="My Item",        # 显示名称
        key="my_item",         # 用于 --check-only 过滤
        passed=ok,             # 是否通过
        detail="...",          # 详情
        expected="...",        # 期望值
        message="...",         # 结果描述
    )
```

2. 在 `run()` 函数的 `steps` 列表中添加一项：
```python
("my_item", "[7/7] My Item ...", lambda: check_my_item()),
```

---

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

- 🐛 报告 Bug → [Issues](https://github.com/AndyAI-COLA/deploy-checker/issues)
- 💡 提建议 → [Discussions](https://github.com/AndyAI-COLA/deploy-checker/discussions)
- 🔧 提交 PR → [Pull Requests](https://github.com/AndyAI-COLA/deploy-checker/pulls)

---

## 📄 License

[MIT License](LICENSE) — 自由使用和修改。
