import re
import requests
from pyquery import PyQuery as pq


class Search(object):

    def __init__(self, quiz, choices):
        self.__quiz = quiz
        self.__choices = choices
        self.__search_list = []
        self.__answer = -1

    def sougou(self):
        search_url = 'http://www.sogou.com/web'
        payload = {'query': self.__quiz}
        answer = ''
        for i in range(0, 4):
            try:
                r = requests.get(search_url, payload, timeout=0.8)
                break
            except Exception as e:
                pass
            if i == 3:
                return ''
        doc = pq(r.text)
        content = doc('.results').remove('#sogou_vr_21421101_sq_ext_10000')
        print(content.text())

    def baidu(self):
        search_url = 'http://www.baidu.com/s'
        payload = {'wd': self.__quiz, 'rn': 25}
        answer = ''
        for i in range(0, 4):
            try:
                headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9;q=0.8', \
                           'Host': 'www.baidu.com', \
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
                r = requests.get(search_url, payload, timeout=0.8)
                break
            except Exception as e:
                pass
            if i == 3:
                return ''
        doc = pq(r.text)
        content = doc('#content_left')
        text1 = content.remove('style').remove('script').remove('.f13').remove('div.c-abstract > span')
        max_num = 0
        min_num = 10000
        answer_max = ''
        answer_min = ''
        for i in self.__choices:
            pattern = re.compile(i)
            tmp_num = len(pattern.findall(text1.text()))
            if(tmp_num > max_num):
                max_num = tmp_num
                answer_max = i
            if(tmp_num < min_num):
                min_num = tmp_num
                answer_min = i
        return answer_min if '不' in self.__quiz or '没' in self.__quiz else answer_max

if __name__ == '__main__':
    print(Search("下列选项中，哪一个城市不属于“七大古都”之一？", ["沈阳", "西安", "南京"]).baidu())


