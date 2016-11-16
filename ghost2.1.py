# -*-coding=utf-8 -*-
"""
贴吧幽灵
"""
import urllib
import urllib2
import re
import cookielib
import time
import redis
import random

name = 'xxxxxx'
host = 'http://tieba.baidu.com'
headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8',
	'Cache-Control':'max-age=0',
	'Connection':'keep-alive',
	'Cookie':'xxxxxx',
	'Host':'tieba.baidu.com',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

#注册Cookies
cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)


#获取需要进入的贴吧地址
def getBarUrl(name):
	pattern = r'160;<a href="(.*?)">' + name + '</a>'
	pattern_head = r'my_love_bar"><a href="(.*?)">'+name+'</a>'

	request = urllib2.Request(host + '/mo/', headers = headers)
	response = urllib2.urlopen(request)
	content = response.read()
	response.close()
	# print content
	try:
		url_bar =host + re.search(pattern, content).group(1)
	except AttributeError:
		url_bar =host + re.search(pattern_head, content).group(1)
	return url_bar
	
def getCode(url):
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    content = response.read()
    response.close()
    return content

#获取首页各个帖子的地址，函数返回一个list
def getList(url, code):	
	temp_url = re.match(r'(.*?)m\?kw',url).group(1)
	list_tie = re.findall(r'<div class="i"><a href="(.*?)">', code)
	list_tie = [temp_url+i for i in list_tie]
	return list_tie

#获取回帖需要的关键字
def getKey(url):
	content = getCode(url)
	ti_value = re.search(r'<input type="hidden" name="ti" value="(.*?)"/>', content)
	src_value = re.search(r'<input type="hidden" name="src" value="(.*?)"/>',content)
	word_value = re.search(r'<input type="hidden" name="word" value="(.*?)"/>',content)
	tbs_value = re.search(r'<input type="hidden" name="tbs" value="(.*?)"/>', content)
	ifpost_value = re.search(r'<input type="hidden" name="ifpost" value="(.*?)"/>', content)
	ifposta_value = re.search(r'<input type="hidden" name="ifposta" value="(.*?)"/>', content)
	post_info_value = re.search(r'<input type="hidden" name="post_info" value="(.*?)"/>', content)
	tn_value = re.search(r'<input type="hidden" name="tn" value="(.*?)"/>', content)
	fid_value = re.search(r'<input type="hidden" name="fid" value="(.*?)"/>', content)
	verify_value = re.search(r'<input type="hidden" name="verify" value="(.*?)"/>', content)
	verify_2_value = re.search(r'<input type="hidden" name="verify_2" value="(.*?)"/>', content)
	pinf_value = re.search(r'<input type="hidden" name="pinf" value="(.*?)"/>', content)
	pic_info_value = re.search(r'<input type="hidden" name="pic_info" value="(.*?)"/>', content)
	z_value = re.search(r'<input type="hidden" name="z" value="(.*?)"/>', content)
	last_value = re.search(r' <input type="hidden" name="last" value="(.*?)"/>', content)
	pn_value = re.search(r'<input type="hidden" name="pn" value="(.*?)"/>', content)
	r_value = re.search(r'<input type="hidden" name="r" value="(.*?)"/>', content)
	see_lz_value = re.search(r'<input type="hidden" name="see_lz" value="(.*?)"/>', content)
	no_post_pic_value = re.search(r'<input type="hidden" name="no_post_pic" value="(.*?)"/>', content)
	floor_value = re.search(r'<input type="hidden" name="floor" value="(.*?)"/>', content)
	keywords = {'ti':ti_value.group(1), 'src':src_value.group(1), 'word':word_value.group(1), 'tbs':tbs_value.group(1), 'ifpost':ifpost_value.group(1), 'ifposta':ifposta_value.group(1), 'post_info':post_info_value.group(1), 'tn':tn_value.group(1), 'fid':fid_value.group(1), 'verify':verify_value.group(1), 'verify_2':verify_2_value.group(1), 'pinf':pinf_value.group(1), 'pic_info':pic_info_value.group(1), 'z':z_value.group(1), 'last':last_value.group(1), 'pn':pn_value.group(1), 'r':r_value.group(1), 'see_lz':see_lz_value.group(1), 'no_post_pic':no_post_pic_value.group(1), 'floor':floor_value.group(1), 'sub1':'回贴'}
	return keywords


def reply(url, url_re, data):
	#构造帖子post目标地址
	url_temp = re.match(r'(.*?)m\?kw', url)
	url_reply = url_temp.group(1) + "submit"
	# print url_reply
	headers['Referer'] = url_re
	request = urllib2.Request(url_reply, headers=headers)
	data_en = urllib.urlencode(data)
	response = opener.open(request, data_en)
	content = response.read()
	headers.pop('Referer')
	response.close()
	return content

#-*-coding=utf-8-*-
def getAnswer():
	import MySQLdb
	try:
		n = 0
		conn = MySQLdb.connect(host='localhost', user='root', passwd='xxx', db='juzimi', charset='utf8')
		cursor = conn.cursor()

		cursor.execute("SELECT id, juzi, author, article FROM juzi order by rand() limit 1")
		a = cursor.fetchone()[1:]
		juzi = a[0].encode('utf-8','ignore')
		author = a[1].encode('utf-8','ignore')
		article = a[2].encode('utf-8','ignore')
		# 判断作者 来源是否为空
		if author=='':
			n = n + 2
		if article=='':
			n = n + 1
		if n==0:
			answer = juzi + '————' + author + '《' + article + '》'
		if n==1:
			answer = juzi + '————' + author
		if n==2:
			answer = juzi + '————' + '《' + article + '》'
		if n==3:
			answer = juzi
		print answer
		return answer
	except:
		print 'error'
		exit()
	finally:
		cursor.close()
		conn.commit()
		conn.close()


u_bar = getBarUrl(name)
c_bar = getCode(u_bar)
list_tie = getList(u_bar, c_bar)

r = redis.Redis(host='localhost',port=6379,db=0)

for i in list_tie:
	ii = re.search(r'm\?kz=(.*?)&', i).group(1)
	if not r.sismember('urls',ii):
		keywords = getKey(i)
		keywords['pinf'] = '1_2_0'	#不知道为什么 这个关键词抓取不到

		myju = getAnswer()	#添加回复内容
		keywords['co'] = str(myju)
		content = reply(u_bar, i, keywords)
		if '您要浏览的贴子不存在' in content:
			print '回复成功.'
		elif '最新回复' in content:
			print '回复成功.'
		else:
			print content
		r.sadd('urls',ii)
		# r.save
		time.sleep(60)
print '========================================================================================='