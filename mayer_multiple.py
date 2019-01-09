#!/bin/python
import datetime
import time
import requests
import re
from lxml import html
import tweepy		# pip install tweepy

all_cryptos = ['bitcoin', 'ethereum'] 
# Only care about ETH and BTC

#functions
def get_coins():
	page = requests.get('https://coinmarketcap.com/all/views/all/')	# List all cryptocurrencies from coinmarketcap.com
	tree = html.fromstring(page.content)
	all_coins = tree.xpath('//a[@class="currency-name-container"]/text()')
	lower_case_list = map(str.lower, all_coins)		# makes all coins lower-case
	corrected_coin_list = [s.replace(' ','-') for s in lower_case_list]	# replaces all spaces with hyphens
	return corrected_coin_list
	
def visit(url):
	visited.add(url)
	extracted_body = requests.get(url).text
	matches = re.findall(http_re, extracted_body)
	for match in matches:
		if match not in visited :
			visit(match)

def build_url(coin):	# This function builds the URLs based on the coin being queried
	prefix = "https://coinmarketcap.com/currencies/"
	startdate = (datetime.datetime.now() - datetime.timedelta(days=200)).date().strftime('%Y%m%d')
	suffix = "/historical-data/?start=" + startdate + "&end=" + datetime.datetime.today().strftime('%Y%m%d')
	new_url = prefix + coin + suffix
	return new_url

def get_current_price(coin):	# This function grabs the current price of the coin being queried
	page = requests.get(build_url(coin))
	tree = html.fromstring(page.content)
	current_price = tree.xpath('//span[@class="text-large2"]/text()')
	return round(float(current_price[0]), 2)

def pull_prices(coin):		# This function retrieves the last 200 days of prices from the coin's page
	page = requests.get(build_url(coin))
	tree = html.fromstring(page.content)
	all_prices = tree.xpath('//td[@data-format-fiat]/text()')
	return all_prices

def mayer_multiple(coin):	# This function calculates the Mayer Multiple for the coin
	closing_prices = pull_prices(coin)[3::4] # filtering the closing prices from the entire list
	moving_avg = sum([float(i) for i in closing_prices])/len(closing_prices)
	m_multiple = get_current_price(coin) / moving_avg
	return round(m_multiple, 2)
	

def tweet_msg(coin, current_price, m_multiple):	# This function tweets a message based on the Mayer Multiple
	if m_multiple < 0.9:
		message = "BUY alert: " + coin + " has a current price of $" + current_price + " and a current mayer multiple of " + str(m_multiple)
		return message
	elif m_multiple > 2.4:
		message = "SHODL alert: " + coin + " has a current price of $" + current_price + " and a current mayer multiple of " + str(m_multiple)
		return message
		quit()
	else:
		quit()

