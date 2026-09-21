# 小学四则运算题目生成器

本项目实现题目生成、精确答案计算和答案批改。运行时只依赖 Python 3.10 及以上版本；所有计算使用 `fractions.Fraction`，不会出现浮点误差。

## 运行

在本目录打开 PowerShell：

```powershell
# 生成 10 道数值范围为 [0, 10) 的题目
python Myapp.py -n 10 -r 10

# Windows 下也可使用批处理入口
.\Myapp.bat -n 10 -r 10

# 批改题目与答案
python Myapp.py -e Exercises.txt -a Answers.txt
```

生成模式在当前工作目录写入 `Exercises.txt` 和 `Answers.txt`；批改模式写入 `Grade.txt`。`-n` 省略时默认为 10，`-r` 在生成模式下必须提供。参数不合法、文件不存在或指定范围无法容纳所需数量时，程序会给出错误并返回非零退出码。

## 设计

- `arithmetic.py`：不可变表达式树、分数格式化、随机生成器、递归下降解析器和批改逻辑。
- `Myapp.py`：命令行参数校验和文件读写。
- `tests/`：核心逻辑和端到端命令行测试。

每个表达式节点在创建时计算精确值。减法节点只在左值不小于右值时创建；除法节点只在结果严格位于 0 和 1 之间时创建。生成器创建 1 至 3 个运算符的树。

判重不按计算结果，而是按表达式结构生成规范键。在每个 `+` 或 `×` 节点中，两个子树的规范键排序，因此交换律得到同一键；树的嵌套关系不被展平，所以不会错误套用结合律。这与题目给出的 `3+(2+1)`、`1+2+3` 和 `3+2+1` 示例一致。

批改模块自行解析整数、普通分数、带分数、括号和四种运算符，没有调用 `eval`。它同时接受题目要求的 Unicode 运算符和常见 ASCII 运算符。

## 测试

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

测试覆盖分数输入输出、优先级、括号、非法分母、减法非负、除法真分数、交换律判重、结合方向、生成约束、文件生成、参数错误、漏答/错答和批改文件等场景。

## 打包为 exe（可选）

```powershell
python -m pip install pyinstaller
pyinstaller --onefile --name Myapp Myapp.py
```

生成的程序位于 `dist/Myapp.exe`，使用方式与 Python 入口相同。
