import uiautomator2 as u2
import search
import database
import time
from log import Logger
from weditor import uidumplib
import re
import random

class Operate(object):

    def __init__(self, device):
        self.__d = u2.connect(device)
        self.__display = self.__d.device_info['display']
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
                    if self.__d(text='玩游戏').click_exists(10):
                        logger.debug('进入游戏页面1')
                        if self.__d(description='答题赢钱').click_exists(10):
                            logger.info('选择游戏')
                        else:
                            logger.warning('选择游戏失败')
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
                elif self.__d(description='/5').exists:
                    logger.warning('游戏已经开始')
                    return True
            if self.__d(description='本场消耗:').wait(False, 10):
                logger.info('匹配成功')
                return True
        else:
            logger.warning('进入排位赛失败')
            return False


    def answer(self):
        try:
            logger.debug('获取题目')
            id, quiz, choices, coordinate_choices, start_time = self.getsubject()
            result = self.get_answer(quiz, choices)
            logger.info('我的答案：%s' % choices[result['answer']])
            mychoice = result['answer']
            all_time = time.clock() - start_time
            #logger.info("耗时：%f s" % all_time)
            #这个方法也容易被封号，需加个随机延时
            time.sleep(0 if all_time > 1.5 else 1.5 - all_time)
            self.__d(description=['A.  ', 'B.  ', 'C.  '][mychoice] + choices[mychoice]).click()
            #此方法速度太快，容易被禁赛
            #self.__d.click(coordinate_choices[mychoice][0], coordinate_choices[mychoice][1])
            logger.debug('选择选项')
            iscorrect, result['answer'] = self.checkup(mychoice, choices)
            if result['answer'] >= 0:
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
        start_time = time.clock()
        dom = uidumplib.get_android_hierarchy_dom(self.__d).documentElement
        node_flag = select(dom, 'content-desc', '/5')
        node_id = node_flag.previousSibling.previousSibling
        node_parent = node_flag.parentNode.previousSibling.previousSibling
        node_quiz = node_parent.childNodes[3]
        node_A = node_parent.childNodes[5].childNodes[1]
        node_B = node_parent.childNodes[7].childNodes[1]
        node_C = node_parent.childNodes[9].childNodes[1]
        id = node_id.attributes.getNamedItem('content-desc').value
        logger.info('第 %s 题' % id)
        quiz = node_quiz.attributes.getNamedItem('content-desc').value
        logger.info(quiz)
        choices = []
        choices.append(node_A.attributes.getNamedItem('content-desc').value[4::])
        choices.append(node_B.attributes.getNamedItem('content-desc').value[4::])
        choices.append(node_C.attributes.getNamedItem('content-desc').value[4::])
        logger.info('A.%s B.%s C.%s' % (choices[0], choices[1], choices[2]))
        pattern = re.compile(r'\d+')
        A_bounds = pattern.findall(node_A.attributes.getNamedItem('bounds').value)
        A_bounds = [int(i) for i in A_bounds]
        B_bounds = pattern.findall(node_B.attributes.getNamedItem('bounds').value)
        B_bounds = [int(i) for i in B_bounds]
        C_bounds = pattern.findall(node_C.attributes.getNamedItem('bounds').value)
        C_bounds = [int(i) for i in C_bounds]
        coordinate_A = [int((A_bounds[0]+A_bounds[2])/2)/self.__display['width'], int((A_bounds[1]+A_bounds[3])/2)/self.__display['height']]
        coordinate_B = [int((B_bounds[0]+B_bounds[2])/2)/self.__display['width'], int((B_bounds[1]+B_bounds[3])/2)/self.__display['height']]
        coordinate_C = [int((C_bounds[0]+C_bounds[2])/2)/self.__display['width'], int((C_bounds[1]+C_bounds[3])/2)/self.__display['height']]
        # tmp = self.__d(className='android.view.View')
        # c = tmp.count
        # id = tmp[c - 2].info['contentDescription']
        # logger.info('第 %s 题' % id)
        # quiz = tmp[c - 6].info['contentDescription']
        # logger.info(quiz)
        # choices = []
        # choices.append(tmp[c - 5].info['contentDescription'][4::])
        # choices.append(tmp[c - 4].info['contentDescription'][4::])
        # choices.append(tmp[c - 3].info['contentDescription'][4::])
        # logger.info('A.%s B.%s C.%s' % (choices[0], choices[1], choices[2]))
        return id, quiz, choices, [coordinate_A, coordinate_B, coordinate_C], start_time

    def checkup(self, mychoice, choices):
        #这部分可以在改进一下
        while True:
            dom = uidumplib.get_android_hierarchy_dom(self.__d).documentElement
            choiceslist = []
            for i in choices:
                node_tmp = select(dom, 'content-desc', ['A.  ', 'B.  ', 'C.  '][mychoice] + choices[mychoice])
                if node_tmp is None:
                    logger.warning('未及时获取结果')
                    return False, -1
                choiceslist.append(node_tmp)
            if choiceslist[mychoice].nextSibling.nextSibling is None:
                continue
            elif choiceslist[mychoice].nextSibling.nextSibling.attributes.getNamedItem('class').value == 'android.view.View':
                logger.info('答案正确')
                return True, mychoice
            elif choiceslist[mychoice].nextSibling.nextSibling.attributes.getNamedItem('class').value == 'android.widget.ImageView':
                for i in range(0, len(choices)):
                    if i != mychoice and self.__d(description=['A.  ', 'B.  ', 'C.  '][i] + choices[i]).sibling().count == 2:
                        logger.warning('答案错误')
                        logger.info('正确答案；%s' % choices[i])
                        return False, i
        # time.sleep(1.5)
        # iscorrect = True
        # tmp = self.__d(description=['A.  ', 'B.  ', 'C.  '][mychoice] + choices[mychoice]).sibling()
        # while tmp.count != 2:
        #     pass
        # if tmp[1].info['className'] != 'android.view.View':
        #     iscorrect = False
        #     logger.info('答案错误')
        #     for i in range(0, len(choices)):
        #         if i != mychoice and self.__d(description=['A.  ', 'B.  ', 'C.  '][i] + choices[i]).sibling().count == 2:
        #             mychoice = i
        #             logger.info('正确答案；%s' % choices[i])
        #             break
        # else:
        #     logger.info('答案正确')
        # return iscorrect, mychoice

    def get_answer(self, quiz, choices):
        answer = {'status': 0, 'answer': 1}
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


def select(node, key, value):
    if node is not None:
        attr = node.attributes
        if attr is not None and attr.getNamedItem(key) is not None and attr.getNamedItem(key).value == value:
            return node
        for n in node.childNodes:
            nl = select(n, key, value)
            if nl is not None:
                return nl
    else:
        return None

if __name__ == '__main__':
    d = u2.connect_usb('VBJDU18422021801')
    start = time.clock()
    dom = uidumplib.get_android_hierarchy_dom(d).documentElement
    print(time.clock() - start)