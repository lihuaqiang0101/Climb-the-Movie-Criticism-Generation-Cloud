import os
import jieba#中文分词库
import pickle#pkl文件库
from pyecharts import Geo#数据可视化工具
from pyecharts import Pie
from pyecharts import Bar
from pyecharts import Line
from scipy.misc import imread
from wordcloud import WordCloud
import csv

with open('name.txt', 'r') as f:
	name = f.read()

'''地理分布图'''
def drawGeo(data, title, savepath='results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	geo = Geo(title, 'data from maoyan', title_color="#fff", title_pos="center", width=1200, height=600, background_color="#404a59")
	attr, value = geo.cast(data)
	geo.add("", attr, value, visual_range=[0, 200], visual_text_color="#fff", symbol_size=15, is_visualmap=True)
	geo.render(os.path.join(savepath, title+'.html'))


'''饼图'''
def drawPie(title, data, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	pie = Pie(title, title_pos='center')
	attrs = [i for i, j in data.items()]
	values = [j for i, j in data.items()]
	pie.add('', attrs, values, is_label_show=True, radius=[30, 50], rosetype="radius", legend_pos="left", legend_orient="vertical")
	pie.render(os.path.join(savepath, '%s.html' % title))


'''柱状图(2维)'''
def drawBar(title, data, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	bar = Bar(title)
	attrs = [i for i, j in data.items()]
	values = [j for i, j in data.items()]
	bar.add('', attrs, values, mark_point=["max"], is_convert=True)
	bar.render(os.path.join(savepath, '%s.html' % title))

def DrawBar(title, data, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	bar = Bar(title)
	attrs = [i for i, j in data.items()]
	values = [j for i, j in data.items()]
	bar.add('', attrs, values, mark_point=["max"])
	bar.render(os.path.join(savepath, '%s.html' % title))


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


'''词云'''
def drawWordCloud(words, title, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	wc = WordCloud(font_path='simkai.ttf', background_color='white',width=1920, height=1080, max_words=100,margin=5, mask=imread('mask.png'))
	# try:
	wc.generate_from_frequencies(words)
	wc.to_file(os.path.join(savepath, title+'.png'))
	# except:
	# 	pass


'''折线图'''
def drawLine(title, data, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	line = Line(title)
	attrs = [i for i, j in data.items()]
	values = [j for i, j in data.items()]
	line.add("", attrs, values, is_smooth=True, mark_point=["max"])
	line.render(os.path.join(savepath, '%s.html' % title))


def sort(d):
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

if __name__ == '__main__':
	with open('comments_data.pkl', 'rb') as f:
		data = pickle.load(f)
	# 地理分布
	geo_data = {}
	for key, value in data.items():
		if value[1]:
			value[1] = value[1].strip(' ')
			if value[1] in geo_data:
				geo_data[value[1]] += 1
			else:
				geo_data[value[1]] = 1
	geo_data_new = [(i, j) for i, j in geo_data.items()]
	drawGeo(geo_data_new, '{}影评作者全国分布图'.format(name))
	'''
	# 男女比例
	'''
	gender_data = {'未知': 0, '男': 0, '女': 0}
	for key, value in data.items():
		if value[0] == 1:
			gender_data['男'] += 1
		elif value[0] == 2:
			gender_data['女'] += 1
		else:
			gender_data['未知'] += 1
	drawPie('{}影评作者男女比例'.format(name), gender_data)
	'''
	# 评分分布
	'''
	score_data = {}
	for key, value in data.items():
		if value[2]:
			if value[2] in score_data:
				score_data[value[2]] += 1
			else:
				score_data[value[2]] = 1
	score_data = dict(sorted(score_data.items(), key=lambda item: item[0]))
	drawBar('{}评分分布'.format(name), score_data)
	'''
	# 词云
	'''
	stopwords = open('./stopwords.txt', 'r', encoding='utf-8').read().split('\n')[:-1]#断词
	stopwords.append('电影')
	texts = [d[1][-2] for d in data.items()]
	words_dict = statistics(texts, stopwords)#词频字典
	#画出词云
	dic,keys,values = sort(words_dict)
	drawWordCloud(dic, '{}影评词云'.format(name), savepath='./results')
	# 评论数量随日期的变化
	comments_count = {}
	for key, value in data.items():
		if value[-1]:
			date = value[-1].split(' ')[0]
			if date in comments_count:
				comments_count[date] += 1
			else:
				comments_count[date] = 1
	drawLine('{}影评数量随日期的变化'.format(name), comments_count)
	f = open('{}影评词频统计.csv'.format(name), 'w', encoding='utf-8')
	filedname = ['词汇', '出现频次']
	writer = csv.DictWriter(f, fieldnames=filedname)
	writer.writeheader()
	writeexcel(writer,keys,values)
