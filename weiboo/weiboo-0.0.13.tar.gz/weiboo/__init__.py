#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'weiboo'
import yaml
import cached_url
import urllib
import re

def isUser(key):
	try:
		int(key)
		return True
	except:
		return False

def getSearchUrl(key):
	if isUser(key):
		user = int(key)
		return 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%d&containerid=107603%d' \
			% (user, user)
	content_id = urllib.request.pathname2url('100103type=1&q=' + key)
	return 'https://m.weibo.cn/api/container/getIndex?containerid=%s&page_type=searchall' % content_id

def clearUrl(url):
	return url.split('?')[0]

def getSingleCount(card):
	try:
		return (int(card['reposts_count']) + 
				int(card['comments_count']) + 
				int(card['attitudes_count']))
	except:
		return 0 # if "该账号被投诉", we don't have those counts

def getCount(card):
	card = card.get('mblog', card)
	count = getSingleCount(card)
	if 'retweeted_status' in card:
		count += getSingleCount(card['retweeted_status']) / 3
	return count

def getTextHash(card):
	result = []
	for x in card.get('text', ''):
		if re.search(u'[\u4e00-\u9fff]', x):
			result.append(x)
			if len(result) > 10:
				break
	return ''.join(result)

def getHash(card):
	card = card.get('mblog', card)
	if card.get('retweeted_status'):
		return getTextHash(card.get('retweeted_status'))
	return getTextHash(card)

def sortedResult(result, key = None):
	to_sort = []
	for url, card in result.items():
		to_sort.append((getCount(card), (url, card)))
	to_sort.sort(reverse=True)
	return [item[1] for item in to_sort]

def getResultDict(content):
	result = {}
	for card in content['data']['cards']:
		if 'scheme' in card:
			url = clearUrl(card['scheme'])
			if '/status/' in url:
				result[url] = card
	return result

def getContent(key, ttl=0, sleep=0): 
	url = getSearchUrl(key)
	content = cached_url.get(url, ttl=ttl, sleep = sleep)
	return yaml.load(content, Loader=yaml.FullLoader)

# result is approximately sorted by like
def search(key, ttl=0, sleep=0): 
	content = getContent(key, ttl, sleep)
	result = getResultDict(content)
	return sortedResult(result, key)

def backfill(key, ttl=0, sleep=10, limit=30):
	base_url = getSearchUrl(key)
	content = cached_url.get(base_url, ttl = ttl, sleep = sleep)
	result_dict = getResultDict(yaml.load(content, Loader=yaml.FullLoader))
	final_result = result_dict
	count = 2
	while result_dict:
		url = base_url + '&page=%d' % count
		content = cached_url.get(url, ttl = ttl, sleep = sleep)
		result_dict = getResultDict(yaml.load(content, Loader=yaml.FullLoader))
		final_result.update(result_dict)
		count += 1
		if count > limit:
			break
	return sortedResult(final_result)

def getPotentialUser(key, card):
	screenname = card.get('user', {}).get('screen_name')
	uid = str(card.get('user', {}).get('id'))
	if key in [uid, screenname] and len(uid) > 3:
		return uid, screenname

def yieldUser(key, content):
	for card in content['data']['cards']:
		yield getPotentialUser(key, card.get('mblog', {}))
		for sub_card in (card.get('card_group') or []):
			yield getPotentialUser(key, sub_card) 

def searchUser(key, sleep=0):
	content = getContent(key, ttl=float('inf'), sleep=sleep)
	for result in yieldUser(key, content):
		if result:
			return result
