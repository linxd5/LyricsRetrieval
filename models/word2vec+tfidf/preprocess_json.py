#!/usr/bin/env python
# coding=utf-8

# 输入数据文件的路径和名字
# 输出处理后的文件

import re, json

def preprocess(file):
    write_file = file + '_processed'
    temp_num = 0
    
    with open(file) as f_read:
        with open(write_file, 'w') as f_write:
            for line in f_read:
                # 匹配歌词和id
                temp = json.loads(line, 'utf-8')
                id, lyrics, temp_dict = temp['id'], temp['lyrics'], {}
                if lyrics:
                    # 替换非中文字符为空格
                    lyrics = re.sub(u'[^\u4e00-\u9fa5]', u' ', lyrics)
                    lyrics = re.sub('\s+', ' ', lyrics)
                    if len(re.sub(u' ', u'', lyrics)) > 30:
                        temp_dict['id'], temp_dict['lyrics'] = id, lyrics
                        # 向文件中写入中文，而不是 Unicode  
                        temp_dict = json.dumps(temp_dict, ensure_ascii=False)
                        f_write.write(temp_dict + '\n')
                    temp_num += 1
                    if temp_num % 10000 == 0:
                        print('+++ Processing song', temp_num)
    return write_file
                    
if __name__ == '__main__':
    file = 'lyrics.json'
    preprocess(file)

    # 这段代码演示了如何读入处理后的数据
    """
    with open('lyrics.json_processed') as file:
        for line in file:
            temp = json.loads(line, 'utf-8')
            print(temp['id'], '   ', temp['lyrics'])
    """
