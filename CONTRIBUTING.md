# 🤝 Contributing Guide

感谢你对 **deploy-checker** 的关注！欢迎任何形式的贡献。

---

## 🚀 快速开始

```bash
# 1. Fork 本仓库
# 2. Clone 你的 Fork
git clone https://github.com/你的用户名/deploy-checker.git
cd deploy-checker

# 3. 创建新分支
git checkout -b feature/你的功能名

# 4. 修改代码并测试
python checker.py

# 5. 提交并推送
git add .
git commit -m "feat: 描述你的改动"
git push origin feature/你的功能名

# 6. 到 GitHub 上发起 Pull Request
```

---

## 📋 贡献类型

### 🐛 Bug 修复
- 发现 Bug？请先在 [Issues](https://github.com/你的用户名/deploy-checker/issues) 中搜索是否已存在
- 如果没有，创建一个新 Issue，描述清楚复现步骤
- 然后 Fork 仓库，修复后提交 PR

### ✨ 新功能
- 想添加新的检查项？参考下方「添加新检查项」章节
- 大型功能建议先开 Issue 讨论

### 📝 文档改进
- 修正错别字、改善说明、添加示例都很欢迎

### 🎨 UI / 体验优化
- 彩色输出改进、新增参数、错误提示优化等

---

## 🔧 添加新的检查项

这是最常见的贡献方式！步骤如下：

### 1. 编写检查函数

在 `checker.py` 中新增一个函数，返回标准格式的 dict：

```python
def check_docker():
    """检查 Docker 是否已安装"""
    try:
        r = subprocess.run(
            ["docker", "--version"],
            capture_output=True, text=True, timeout=10
        )
        ver = r.stdout.strip()
        ok = bool(ver)
        return dict(
            name="Docker",
            key="docker",
            passed=ok,
            detail=ver if ok else "Not installed",
            expected="Installed",
            message=ver if ok else "Docker not found"
        )
    except FileNotFoundError:
        return dict(
            name="Docker", key="docker", passed=False,
            detail="Not installed", expected="Installed",
            message="Docker not found"
        )
    except subprocess.TimeoutExpired:
        return dict(
            name="Docker", key="docker", passed=False,
            detail="Timeout", expected="Installed",
            message="Timeout"
        )
```

### 2. 注册到 steps 列表

在 `run()` 函数的 `steps` 列表中添加：

```python
steps = [
    # ... 已有的检查项 ...
    ("docker",  "[7/7] Docker ..........",  lambda: check_docker()),
]
```

### 3. 更新 README

在「检查项目说明」表格中添加新行：

```markdown
| Docker | `docker` | 检查是否安装 | 能输出版本号即通过 |
```

---

## 📏 代码规范

| 项目 | 要求 |
|------|------|
| Python 版本 | ≥ 3.8 |
| 编码 | UTF-8 |
| 缩进 | 4 空格 |
| 行宽 | 建议 ≤ 100 字符 |
| 风格 | 遵循 PEP 8 |
| 依赖 | 仅使用 Python 标准库 |

---

## ✅ 提交前检查清单

- [ ] `python checker.py` 能正常运行
- [ ] `python checker.py -c 你新增的key` 能正常运行
- [ ] 新增检查项有清晰的 docstring
- [ ] README 中的表格已更新
- [ ] 没有提交任何临时文件（.log、.json、__pycache__）
- [ ] Commit message 遵循格式（见下方）

---

## 📝 Commit Message 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>: <description>
```

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响逻辑） |
| `refactor` | 重构（不新增功能、不修复 Bug） |
| `test` | 添加测试 |
| `chore` | 构建、工具链等杂项 |

**示例：**
```
feat: add Docker installation check
fix: handle timeout on slow networks
docs: update contributing guide
```

---

## ❓ 有问题？

在 [Issues](https://github.com/你的用户名/deploy-checker/issues) 中提问即可，我会尽快回复。

---

感谢你的贡献！🎉
