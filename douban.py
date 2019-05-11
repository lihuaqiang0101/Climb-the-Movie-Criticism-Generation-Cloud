import requests
from bs4 import BeautifulSoup
import re
from pyecharts import Line
from pyecharts import Bar
from pyecharts import Pie
import os
import jieba
from wordcloud import WordCloud
from scipy.misc import imread
import csv

if not os.path.exists('./results'):
    os.mkdir('./results')

id = input('请输入电影id：')
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
    }

def DrawPie(title, data, savepath='./results'):
	pie = Pie(title)
	attrs = data[:5]
	values = data[5:]
	pie.add('', attrs, values, is_label_show=True)
	pie.render(os.path.join(savepath, '%s.html' % title))

'''折线图'''
def drawLine(title, data, savepath='./results'):
	line = Line(title)
	attrs = data[:len(data)//2]
	values = data[len(data)//2:]
	line.add("", attrs, values, is_smooth=True, mark_point=["max"])
	line.render(os.path.join(savepath, '%s.html' % title))

#统计一个列表中各元素出现的频次返回一个字典
def all_list(arr):
    result = {}
    for i in set(arr):
        result[i] = arr.count(i)
    return result

'''统计词频'''
def statistics(texts, stopwords):
	words_dict = {}
	for text in texts:
		#将一段话分成一个个有意义的词语
		#将字符串分隔成词语数组并返回
		temp = jieba.cut(text)
		for t in temp:#t是分割出的词语
			#判断t是否是断词
			if t in stopwords:
				continue
			if t in words_dict.keys():
				words_dict[t] += 1
			else:
				words_dict[t] = 1
	return words_dict

def DrawBar(title, data, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	bar = Bar(title)
	attrs = [i for i, j in data.items()]
	values = [j for i, j in data.items()]
	bar.add('', attrs, values, mark_point=["max"])
	bar.render(os.path.join(savepath, '%s.html' % title))

'''词云'''
def drawWordCloud(words, title, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	wc = WordCloud(font_path='simkai.ttf', background_color='white',width=1920, height=1080, margin=5, mask=imread('mask.png'))
	wc.generate_from_frequencies(words)
	wc.to_file(os.path.join(savepath, title+'.png'))

def sort(d,name):
	keys = sorted(d, key=lambda k: d[k], reverse=True)
	values = []
	for key in keys:
		values.append(d[key])
	dic = {}
	dicbar = {}
	for i in keys[:1002]:
		dic[i] = d[i]
	try:
		del dic['\n']
		del dic['…']
	except:
		pass
	for i in keys[:22]:
		dicbar[i] = d[i]
	try:
		del dicbar['\n']
		del dicbar['…']
	except:
		pass
	DrawBar(title='{}高频词汇统计'.format(name), data=dicbar)
	return dic,keys,values

def writeexcel(writer,keys,values):
	for i in range(len(keys)):
		wordfrequency = {'词汇': keys[i], '出现频次': values[i]}
		writer.writerow(wordfrequency)

grades = []
dates = []
for i in range(11):
    url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&sort=new_score&status=P'.format(id,i*20)
    try:
        response = requests.get(url, headers=headers)
    except:
        pass
    text = response.content.decode('utf-8')
    soup = BeautifulSoup(text, 'html5lib')
    if i == 0:
        div = soup.find('div',id='content')
        h1 = div.find('h1')
        name = h1.text.split(' ')[0]
        f = open('{}影评.txt'.format(name),'w',encoding='utf-8')
    divs = soup.find_all('div', class_='comment-item')
    for div in divs:
        span = div.find('span',class_='comment-info')
        spans = span.find_all('span')
        if len(spans)==3:
            grade = spans[1]['class'][0]
            grade = re.findall(r'[0-9]',grade)[0]#评分
            grades.append(grade)
            dates.append(spans[2].text.strip())#日期
        text = div.find('p').text.strip()
        f.write(text)#影评
        f.write('\n')
f.close()
data = list(all_list(grades).keys())
data.extend(list(all_list(grades).values()))
date = list(all_list(dates).keys())
date.extend(list(all_list(dates).values()))
drawLine('{}影评数量随日期的变化'.format(name), date)
DrawPie('{}评分分布统计饼图'.format(name),data)
stopwords = open('./stopwords.txt', 'r', encoding='utf-8').read().split('\n')[:-1]#断词
stopwords.append('电影')
with open('{}影评.txt'.format(name),'r',encoding='utf-8') as f:
    texts = f.readlines()
words_dict = statistics(texts, stopwords)#词频字典
dic,keys,values = sort(words_dict,name)
drawWordCloud(dic, '{}影评词云'.format(name), savepath='./results')
f = open('{}影评词频统计.csv'.format(name), 'w', encoding='utf-8')
filedname = ['词汇', '出现频次']
writer = csv.DictWriter(f, fieldnames=filedname)
writer.writeheader()
writeexcel(writer,keys,values)
