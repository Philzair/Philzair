论文查重程序 README

## 一、项目简介

实现一个简易论文查重程序，比较原文与抄袭版论文，输出重复率。

命令行格式：

```bash
python main.py <原文文件> <抄袭版论文文件> <答案文件>
答案文件输出浮点型重复率，精确到小数点后两位，例如 0.82。

二、运行环境
Python 3.8+

无第三方运行依赖，仅使用标准库

测试依赖：pytest、pytest-cov、flake8、pylint

三、算法简介
读取文件，按 UTF-8 解码，忽略非法字符；

清洗文本：去除 HTML 标签、script/style、标点、空白，只保留中文、英文、数字；

提取字符 unigram 和 bigram 频率；

分别计算 unigram 和 bigram 的余弦相似度；

加权求和：0.4 * unigram + 0.6 * bigram，保留两位小数输出。

四、核心接口
text
main.py
├── read_text(path)              读取文件
├── preprocess(text)             文本清洗
├── char_ngrams(text, n)         提取 n-gram
├── cosine_similarity(c1, c2)    余弦相似度
├── calculate_similarity(orig, copy)  核心计算
├── write_answer(ans_path, sim)  写答案文件
└── main(argv)                   命令行入口
五、性能改进
使用 cProfile 分析，耗时主要在 preprocess 和 char_ngrams。
改进措施：

预编译正则表达式；

使用 Counter 统计词频；

减少重复遍历，一次提取特征；

预处理阶段直接删除标点和空白。

典型样例运行时间小于 1 秒，内存远低于 2048MB。

六、单元测试
运行：

bash
pytest --cov=. --cov-report=html
测试用例（至少 10 个）：

测试	说明
相同文件	相似度 1.00
完全不同	相似度接近 0
原文空	相似度 0
抄袭文空	相似度 0
增删改	相似度合理
HTML 清洗	标签不影响
文件不存在	抛出异常
预处理去标点	只留有效字符
n-gram 提取	bigram 正确
余弦相似度	相同向量为 1
命令行正常	返回 0，答案正确
参数错误	返回非零，不崩溃
覆盖率截图见 docs/coverage.png。

七、异常处理
异常	场景	处理
参数数量错误	不传参数	提示用法，返回 2
FileNotFoundError	文件不存在	提示，返回 1
UnicodeDecodeError	编码错误	忽略非法字符，不崩溃
PermissionError	无权限	提示，返回 1
空文件	原文或抄袭文为空	相似度返回 0
写入失败	答案路径不可写	提示，返回 1
原则：不异常退出，信息明确，正常输入不受影响。

八、PSP 表格
PSP2.1	阶段	预估（分钟）	实际（分钟）
Planning	计划	30	25
Development	开发	370	410
· Analysis	需求分析	60	70
· Design	具体设计	30	25
· Coding	具体编码	180	220
· Test	测试	80	90
Reporting	报告	90	85
合计		490	520
九、总结
本项目完成了一个基于 Python3 的论文查重程序，支持命令行输入输出，输出两位小数相似度。算法采用文本清洗、字符 unigram + bigram 加权余弦相似度，能处理增删改、乱序及 HTML 残留。使用 pytest 完成 10 个以上单元测试，cProfile 进行性能优化。不足是对语义改写识别有限，后续可引入 TF-IDF 或词向量。