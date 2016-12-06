#!/usr/bin/env python
# coding=utf-8

# 输入处理后的中文歌词文件
# 输出中文歌词的分词结果,并保存在文件中

import jieba
import json

def jieba_seg(file):
    write_file = file + '_jieba'
    temp_num = 0

    with open(file) as f_read:
        with open(write_file, 'w') as f_write:
            for line in f_read:
                # 得到歌词和id
                temp = json.loads(line, 'utf-8')
                id, lyrics, temp_dict = temp['id'], temp['lyrics'], {}
                seg_list = jieba.lcut(lyrics, cut_all=False)
                temp_dict['id'], temp_dict['lyrics_jieba'] = id, seg_list
                # 向文件中写入中文，而不是 Unicode
                temp_dict = json.dumps(temp_dict, ensure_ascii=False)
                f_write.write(temp_dict + '\n')

                temp_num += 1
                print('+++ Processing song', temp_num)
    return write_file

if __name__ == "__main__":

    file = 'lyrics.json_processed'
    jieba_seg(file)

    # 测试代码
    """
    with open('lyrics.json_processed_jieba') as file:
        for line in file:
            temp = json.loads(line, 'utf-8')
            print(temp['id'], temp['lyrics_jieba'])
    """
