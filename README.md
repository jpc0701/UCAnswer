# UCAnswer
中秋节假在家两天，无聊写了个UC浏览器的全民答题辅助

之前过年的时候，答题活动很火啊，答题类辅助也有很多。他们主要是利用网络抓包，嗅探app 的报文，获取题目的内容和选项。之后进行搜索答案，写入数据库。

但是，后来app的报文加密了，不是明文传输了，然后就有人开始利用ocr识别文字，但是速度不仅下降了，而且识别率也有问题。

此项目利用测试框架，获取当前屏幕的控件信息，就可以比较快速准确的获取题目内容。

使用的框架是uimatomator，github：https://github.com/openatx/uiautomator2

version 1.0
直接使用uiautomator2的基本功能，定位元素，获取题目内容

version 2.0
除了使用uiautomator2的基本功能外，在获取题目内容方面改写了一点内容，使获取题目内容速度大大增加，但是这样答题速度太快了，容易被发现禁赛，所以要加个随机延时的函数。
