#!/usr/bin/env python
# coding=utf-8

# 输入数据文件的路径和名字
# 输出处理后的文件


import re

def preprocess(file):
    write_file = file + '_processed'
    temp_num = 0
    with open(file) as f_read:
        with open(write_file, 'w') as f_write:
            for line in f_read:
                # 匹配歌词字段
                matchObj = re.match(r'.*"lyrics":"(.*?)"}', line, re.M|re.I)

                if matchObj and matchObj.group(1):
                    # 替换非中文字符为空格
                    song = re.sub(u'[^\u4e00-\u9fa5]', u' ', matchObj.group(1))
                    song = re.sub('\s+', ' ', song)
                    if len(re.sub(u' ', u'', song)) > 30:
                        f_write.write(song + '\n')

                temp_num += 1
                print('+++ Processing song', temp_num)

if __name__ == '__main__':
    file = 'lyrics.json'
    preprocess(file)
