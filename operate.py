import uiautomator2 as u2
import search
import database
import time
from log import Logger
from weditor import uidumplib


class Operate(object):

    def __init__(self, device):
        self.__d = u2.connect_usb(device)
        global logger
        logger = Logger(device)

    def open_game(self):
        self.__d.app_stop('com.UCMobile')
        logger.info('停止UC浏览器')
        if self.__d.press('home'):
            logger.debug('返回主页面')
            if self.__d(text='UC浏览器').click_exists(10):
                logger.debug('打开UC浏览器')
                if self.__d(text='我 的').click_exists(10):
                    logger.debug('进入用户页面')
                    if self.__d(text='赚金币').click_exists(10):
                        logger.debug('进入游戏页面1')
                        if self.__d(description='小游戏赢钱').click_exists(10):
                            logger.debug('进入游戏页面2')
                            if self.__d(description='答题赢钱').click_exists(10):
                                logger.info('选择游戏')
                            else:
                                logger.warning('选择游戏失败')
                        else:
                            logger.warning('进入游戏页面2失败')
                    else:
                        logger.warning('进入游戏页面1失败')
                else:
                    logger.warning('进入用户页面失败')
            else:
                logger.warning('打开UC浏览器失败')
        else:
            logger.warning('返回主页面失败')
        return False

    def rank_game(self):
        if self.__d(description='排位赛').click_exists(10):
            logger.info('进入排位赛')
            logger.info('正在匹配中......')
            while not self.__d(description='本场消耗:').exists:
                if self.__d(description='游戏已结束').exists:
                    self.__d(description='我知道了').click()
                    logger.warning('匹配失败')
                    return False
            if self.__d(description='本场消耗:').wait(False, 10):
                logger.info('匹配成功')
                return True
        else:
            logger.warning('进入排位赛失败')
            return False


    def answer(self):
        try:
            logger.debug('获取题目')
            id, quiz, choices = self.getsubject()
            result = self.get_answer(quiz, choices)
            logger.info('我的答案：%s' % choices[result['answer']])
            mychoice = result['answer']
            self.__d(description=['A.  ', 'B.  ', 'C.  '][mychoice] + choices[mychoice]).click()
            logger.debug('选择选项')
            iscorrect, result['answer'] = self.checkup(mychoice, choices)
            self.update(iscorrect, result, quiz, choices)
            while self.__d(description='/5').exists:
                pass
            logger.info('本题结束')
        except u2.UiObjectNotFoundError as e:
            logger.error(e)
        if id == '5':
            return False
        else:
            return True

    def complete(self):
        i = 0
        while self.answer():
            i += 1
            if i >= 5:
                break

    def rank(self):
        while True:
            if self.rank_game():
                self.complete()
                self.__d(description='继续对战').wait(True, 10)
                try:
                    result = self.__d(descriptionMatches='第\d名：\d{1,4}分').info['contentDescription']
                    logger.info("比赛结果：%s" % result)
                except Exception as e:
                    logger.error("获取比赛结果失败")
                time.sleep(1)
                logger.info('本场比赛结束')
            self.__d.press("back")
            logger.info('返回游戏页面')
            time.sleep(1)

    def getsubject(self):
        while not self.__d(description='/5').exists:
            pass
        tmp = self.__d(className='android.view.View')
        c = tmp.count
        id = tmp[c - 2].info['contentDescription']
        logger.info('第 %s 题' % id)
        quiz = tmp[c - 6].info['contentDescription']
        logger.info(quiz)
        choices = []
        choices.append(tmp[c - 5].info['contentDescription'][4::])
        choices.append(tmp[c - 4].info['contentDescription'][4::])
        choices.append(tmp[c - 3].info['contentDescription'][4::])
        logger.info('A.%s B.%s C.%s' % (choices[0], choices[1], choices[2]))
        return id, quiz, choices

    def checkup(self, mychoice, choices):
        time.sleep(1.5)
        iscorrect = True
        tmp = self.__d(description=['A.  ', 'B.  ', 'C.  '][mychoice] + choices[mychoice]).sibling()
        while tmp.count != 2:
            pass
        if tmp[1].info['className'] != 'android.view.View':
            iscorrect = False
            logger.info('答案错误')
            for i in range(0, len(choices)):
                if i != mychoice and self.__d(description=['A.  ', 'B.  ', 'C.  '][i] + choices[i]).sibling().count == 2:
                    mychoice = i
                    logger.info('正确答案；%s' % choices[i])
                    break
        else:
            logger.info('答案正确')
        return iscorrect, mychoice

    def get_answer(self, quiz, choices):
        answer = {'status': 0, 'answer': 0}
        db = database.UCanswer()
        result = db.search(quiz)
        db.close()
        for choice in choices:
            if choice in result:
                logger.debug('数据库中检索答案')
                answer['status'] = 2
                answer['answer'] = choices.index(choice)
                return answer
        result = search.Search(quiz, choices).baidu()
        if result != '':
            logger.debug('在线检索答案')
            answer['status'] = 1
            answer['answer'] = choices.index(result)
        else:
            logger.debug('未检索到答案')
        return answer

    def update(self, iscorrect, result, quiz, choices):
        db = database.UCanswer()
        if result['status'] <= 1:
            logger.debug('添加此题')
            db.insert(quiz, choices[result['answer']])
        elif not iscorrect:
            logger.debug('更新答案')
            db.update(quiz, choices[result['answer']])
        db.close()


if __name__ == '__main__':
    d = u2.connect_usb('VBJDU18422021801')
    s = time.clock()
    a = uidumplib.get_android_hierarchy(d)
    print(time.clock() - s)