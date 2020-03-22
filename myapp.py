import pandas as pd
import os
import numpy as np

enterStr = '肝'
FeatureNum = 4
Questions = {'Sleeptime': "你一天平均睡几个小时?（请回复阿拉伯数字）",
             'Credits': "你这学期选了多少个学分的课？（请回复阿拉伯数字）",
             'Research': "你参加了几项科创赛事/科研活动？（请回复阿拉伯数字）",
             'Work': "你参与了几个社会工作？（请回复阿拉伯数字）"}


def mkdir(path):
    # 引入模块

    # 去除首位空格
    path = path.strip()
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


class GanResponse:
    def __init__(self, username):
        self.user = username

    def initiate_data(self):
        # 定义要创建的目录
        csvpath = 'data/' + self.user + '/gan.csv'
        test_dict = {'Sleeptime': [-1, ], 'Credits': [-1, ], 'Research': [-1, ], 'Work': [-1, ]}
        df = pd.DataFrame(test_dict)
        # print(df)
        mkdir('data/')
        mkdir('data/' + self.user)
        df.to_csv(csvpath, index=False)

    def judge(self, text):
        if text == enterStr:  # 想进入问题
            csvpath = 'data/' + self.user + '/gan.csv'
            if os.path.exists(csvpath):
                return -1      # 返回“已经参加过本项活动，不要试图重新开始”
            else:
                mkdir('data/' + self.user)
                return -5   # 进入问题

        else:   # 已进行到中间阶段 或 没进行到中间阶段在这里乱涂乱画的
            csvpath = 'data/' + self.user + '/gan.csv'
            if os.path.exists(csvpath):   # 判断文件是否存在，判断进行到了第几阶段
                df = pd.read_csv(csvpath)

                item_n = 0    # 从第0列开始检测
                for item in df.columns:
                    if df.loc[0, item] == -1:
                        break
                    else:
                        item_n += 1
                if item_n == FeatureNum:  # 已经填完表，就不要再捣乱了
                    return -2       # 已填完表，返回“捣乱”错误
                return item_n    # 返回到填写的位置（即第几项）

            else:    # 没填过表，就是来捣乱的
                return -2   # 返回“捣乱”错误

    def write(self, item_n, data):    # 将data写入表格中
        csvpath = 'data/' + self.user + '/gan.csv'
        df = pd.read_csv(csvpath)
        try:
            data = eval(data)
            indexj = df.columns[item_n]
            df.loc[0, indexj] = data
            df.to_csv(csvpath, index=False)
            return item_n + 1      # 返回状态：该填写第item_n+1项了
        except:
            return -4  # 返回“输入格式不符合要求错误”

    def load_result(self):
        csvpath = 'data/' + self.user + '/gan.csv'
        df = pd.read_csv(csvpath)
        score = 0
        score += (24 - df.loc[0, 'Sleeptime']) /15 * 20
        score += df.loc[0, 'Credits'] / 32 * 30
        score += df.loc[0, 'Research'] / 2 * 40
        score += df.loc[0, 'Work'] / 2 * 10

        np.savetxt('data/' + self.user + '/score.txt', [score])
        if os.path.exists('data/data.txt'):
            data = np.loadtxt('data/data.txt')
            data = np.concatenate((data, [score]))
            np.savetxt('data/data.txt', data)
        else:
            mkdir('data')
            np.savetxt('data/data.txt', [score])
        return score

    def load_whole_result(self):
        datapath = 'data/data.txt'
        resultpath = 'data/' + self.user + '/score.txt'
        if os.path.exists(resultpath) and os.path.exists(datapath):    # 个人总数据和全体总数据都要有
            current = np.loadtxt(resultpath)
            grossdata = np.loadtxt(datapath)
            position = np.searchsorted(grossdata, current)
            personnum = grossdata.shape[0]
            avg = grossdata.sum() / personnum

            return [personnum, position/personnum, avg]

        else:
            return -2   # 返回没填过表的错误

    def createResponse(self, text):

        if text == 'm':        # 回复m是查询指令
            try:
                result = self.load_whole_result()
                avgMessage = '\n目前所有人的平均分为{:.2f}'.format(result[2])
                return '目前已经有' + str(result[0]) + '人参与本次活动.\n你的爆肝时间已经打败了{:.2f}%的人'.format(100*result[1]) + avgMessage
            except:
                return "你还没回答完所有问题！"

        statecode = self.judge(text)
        if statecode == -3:
            return "你已经参与过本项活动了，注意查询指令为'm'"
        elif statecode == -2:  # 捣乱错误
            return -1   # 返回-1代表无回应
        elif statecode == -1:
            tempReply = "已经参加过本项活动，不要试图重新开始!\n"        # 应当继续检测答到了哪一道题
            judgeResult = self.judge('5')    # 随便输入一个符合要求的数值以检测答到了第几道题
            if judgeResult == -2:
                return tempReply + "你已经参与完整本项活动了，注意查询指令为'm'"
            else:
                csvpath = 'data/' + self.user + '/gan.csv'
                df = pd.read_csv(csvpath)
                return tempReply + Questions[df.columns[0]]

        else:       # 此时代表处于某个问题中
            if statecode == -5:  # 如果刚问问题
                self.initiate_data()
                csvpath = 'data/' + self.user + '/gan.csv'
                df = pd.read_csv(csvpath)
                return Questions[df.columns[0]]  # 正常情况下返回该写入的项

            csvpath = 'data/' + self.user + '/gan.csv'
            df = pd.read_csv(csvpath)
            columns = df.columns  # 读取dataframe中的列的顺序
            write_result = self.write(statecode, text)
            if write_result == FeatureNum:  # 如果已经填完
                myscore = self.load_result()
                reply = "你填完了所有的项目，你的爆肝分数为：{:.2f}".format(myscore)
                result = self.load_whole_result()
                if result == -2:
                    return "??等会，我的程序出错了"
                reply2 = '\n目前已经有' + str(result[0]) + '人参与本次活动.\n你的爆肝时间已经打败了{:.2f}%的人'.format(100 * result[1])
                reply3 = '\n目前所有人的平均分为{:.2f}'.format(result[2])
                return reply + reply2 + reply3

            if write_result == -4:
                return "你的输入不符合要求，要回复阿拉伯数字"

            return Questions[columns[write_result]]  # 正常情况下返回该写入的项


def welcome():
    welcome_list = ['你好！', 'Hello!', 'Здравствыйте!', '안녕하세요!', 'こんにちは！', 'Ciao!']
    index = np.random.randint(1, 10000) % len(welcome_list)
    return welcome_list[index]


def response(user, text):
    text = text.strip()
    gan = GanResponse(user)
    ganresponse = -1
    try:
        ganresponse = gan.createResponse(text)
    except:
        pass
    if ganresponse == -1:
        return welcome()
    else:
        return ganresponse

