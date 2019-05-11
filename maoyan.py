import re
import time
import json
import pickle
import random
import datetime
import requests
from bs4 import BeautifulSoup

'''
Function:
	爬虫类
'''
class Spider():
	def __init__(self):
		self.info = '猫眼电影评论爬虫'
		#影评url
		self.json_url = "http://m.maoyan.com/mmdb/comments/movie/{}.json?v=yes&offset={}&startTime="
		self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

	'''开始爬取'''
	def start(self, url, num_retries=3):
		film_id = url.split('/')[-1]#拿到电影id
		#获取开始爬取的时间
		res = requests.get(url, headers=self.headers)
		text = res.content.decode('utf-8')
		soup = BeautifulSoup(text, 'lxml')
		Name = soup.find('h3', class_='name')
		self.name = Name.text
		all_data_dict = {}
		for page in range(50):
			json_url = self.json_url.format(film_id, 15*page)
			res = requests.get(json_url, headers=self.headers)
			try:
				res = requests.get(json_url, headers=self.headers)
			except:
				num_retries -= 1
				if num_retries < 0:
					break
			if res.status_code == 200:
				content = res.content
			else:
				content = None
			if content:
				data = self.__parse_data(content)
				if data:
					all_data_dict = dict(all_data_dict, **data)
			time.sleep(1 + random.random())
		f = open('comments_data.pkl', 'wb')
		pickle.dump(all_data_dict, f)
	'''数据解析'''
	def __parse_data(self, data):
		data_temp = json.loads(data, encoding='utf-8').get('cmts')
		data = {}
		if data_temp:
			for dt in data_temp:
				# 昵称
				nickName = dt.get('nickName')
				# 性别
				gender = dt.get('gender')#1代表男性2代表女性
				# 评论内容
				content = dt.get('content')
				print(content)
				# 时间
				start_time = dt.get('startTime')
				# 城市
				city_name = dt.get('cityName')
				# 评分
				score = dt.get('score')
				data[nickName] = [gender, city_name, score, content, start_time]
		return data


if __name__ == '__main__':
	id = input('请输入电影的id：')
	url = 'https://maoyan.com/films/{}'.format(id)
	spider = Spider()
	spider.start(url)
	name = spider.name
	with open('name.txt','w') as f:
		f.write(name)
