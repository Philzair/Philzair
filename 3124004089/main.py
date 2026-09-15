#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文查重程序
用法: python main.py <原文文件> <抄袭版论文文件> <答案文件>
输出: 答案文件中写入浮点型重复率，精确到小数点后两位
"""

import sys
import re
import html
import math
from collections import Counter

# 预编译正则表达式，提高性能
SCRIPT_STYLE_RE = re.compile(r'<(script|style).*?</\1>', re.S | re.I)
TAG_RE = re.compile(r'<[^>]+>')
# 只保留中文、英文字母、数字，其余字符全部删除
CLEAN_RE = re.compile(r'[^\u4e00-\u9fffa-zA-Z0-9]+')


def read_text(path: str) -> str:
    """读取文件内容，忽略编码错误。"""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def preprocess(text: str) -> str:
    """
    文本预处理：
    1. 去除 script/style 标签及内容
    2. 去除所有 HTML 标签
    3. 解码 HTML 实体
    4. 去除非中英文数字字符（标点、空白等）
    """
    # 去除 script 和 style 标签及其内容
    text = SCRIPT_STYLE_RE.sub('', text)
    # 去除所有 HTML 标签
    text = TAG_RE.sub('', text)
    # 解码 HTML 实体，如 &nbsp; &lt; 等
    text = html.unescape(text)
    # 去除非中英文数字字符，只保留中文、英文字母、数字
    text = CLEAN_RE.sub('', text)
    # 去除所有空白字符（包括空格、换行、制表符等）
    text = re.sub(r'\s+', '', text)
    return text


def char_ngrams(text: str, n: int = 2) -> Counter:
    """返回文本的字符 n-gram 频率 Counter。"""
    if n == 1:
        return Counter(text)
    return Counter(text[i:i + n] for i in range(len(text) - n + 1))


def cosine_similarity(c1: Counter, c2: Counter) -> float:
    """计算两个 Counter 的余弦相似度。"""
    if not c1 or not c2:
        return 0.0

    # 计算点积
    dot = sum(c1[k] * c2.get(k, 0) for k in c1)
    # 计算模长
    norm1 = math.sqrt(sum(v * v for v in c1.values()))
    norm2 = math.sqrt(sum(v * v for v in c2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)


def calculate_similarity(orig_path: str, copy_path: str) -> float:
    """计算两个文件的相似度，返回保留两位小数的浮点数。"""
    orig_raw = read_text(orig_path)
    copy_raw = read_text(copy_path)

    orig_text = preprocess(orig_raw)
    copy_text = preprocess(copy_raw)

    # 若任一文本为空，相似度为 0
    if not orig_text or not copy_text:
        return 0.0

    # 提取 unigram 和 bigram
    uni1 = char_ngrams(orig_text, 1)
    uni2 = char_ngrams(copy_text, 1)
    bi1 = char_ngrams(orig_text, 2)
    bi2 = char_ngrams(copy_text, 2)

    sim_uni = cosine_similarity(uni1, uni2)
    sim_bi = cosine_similarity(bi1, bi2)

    # 加权：bigram 权重更高，因为它包含顺序信息
    similarity = 0.4 * sim_uni + 0.6 * sim_bi

    # 保留两位小数
    return round(similarity, 2)


def write_answer(ans_path: str, similarity: float) -> None:
    """将相似度写入答案文件，保留两位小数。"""
    with open(ans_path, 'w', encoding='utf-8') as f:
        f.write(f"{similarity:.2f}\n")


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv

    # 检查命令行参数数量
    if len(argv) != 4:
        print("Usage: python main.py <原文文件> <抄袭版论文文件> <答案文件>", file=sys.stderr)
        return 2

    orig_path, copy_path, ans_path = argv[1], argv[2], argv[3]

    try:
        similarity = calculate_similarity(orig_path, copy_path)
    except FileNotFoundError as e:
        print(f"文件不存在: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"文件无权限: {e}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        print(f"文件编码错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"计算相似度时发生错误: {e}", file=sys.stderr)
        return 1

    try:
        write_answer(ans_path, similarity)
    except OSError as e:
        print(f"写入答案文件失败: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())