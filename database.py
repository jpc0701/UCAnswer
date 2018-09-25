import sqlite3

class UCanswer(object):

    def __init__(self):
        self.__conn = sqlite3.connect('UCANSWER')

    def search(self, quiz):
        c = self.__conn.cursor()
        cursor = c.execute('''select * from SUBJECT WHERE QUIZ = ?;''', (quiz, ))
        answer = []
        for row in cursor:
            answer.append(row[2])
        return answer

    def insert(self, quiz, answer):
        c = self.__conn.cursor()
        c.execute('''insert into SUBJECT (QUIZ, ANSWER) values (?, ?);''', (quiz, answer))
        self.__conn.commit()

    def update(self, quiz, answer):
        c = self.__conn.cursor()
        c.execute('''update SUBJECT set ANSWER = ? where QUIZ = ?;''', (answer, quiz))
        self.__conn.commit()

    def close(self):
        self.__conn.close()

if __name__ == '__main__':
    u = UCanswer()
    print(u.search("'1234'"))