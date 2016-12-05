#!/usr/bin/env python
# coding=utf-8

# 输入数据文件的路径和名字
# 输出处理后的数据

import re


def preprocess(file):
    num = 0
    with open(file) as f:
        for line in f:
            num += 1
            matchObj = re.match('"lyrics":"(.*?)"}', line, re.M|re.I)
            if matchObj:
                print("matchObj.group(2): ", matchObj.group(2))
            print(line)
            if num > 100:
                break


file = "lyrics.json"

preprocess(file)
