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
	
def get_api(cfg):	# provided by http://nodotcom.org/python-twitter-tutorial.html
	auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
 	auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	return tweepy.API(auth)

def tweet_msg(coin, current_price, m_multiple):	# This function tweets a message based on the Mayer Multiple
	if m_multiple < 0.9:
		message = "BUY alert: " + coin + " has a current price of $" + current_price + " and a current mayer multiple of " + str(m_multiple)
		return message
	elif m_multiple > 2.4:
		message = "SELL alert: " + coin + " has a current price of $" + current_price + " and a current mayer multiple of " + str(m_multiple)
		return message
	else:
		return

def main():
	# Fill in the values noted in previous step here --- This was copied from http://nodotcom.org/python-twitter-tutorial.html
	cfg = { 
		"consumer_key"        : "VALUE",
		"consumer_secret"     : "VALUE",
		"access_token"        : "VALUE",
		"access_token_secret" : "VALUE" 
	}

	api = get_api(cfg)

	while True:
		undervalued = []
		overvalued = []
		for crypto in all_cryptos[:200]:
			current_coin = str(crypto)
			if len(pull_prices(current_coin)) < 800:
				time.sleep(.5)
			else:
				current_price = str(get_current_price(current_coin))
				m_multiple = mayer_multiple(current_coin)

				if m_multiple < 0.9:
					tweet = tweet_msg(current_coin, current_price, m_multiple)
					status = api.update_status(status=tweet)
					print "Just tweeted: " + tweet
					if current_coin not in undervalued:
						undervalued.append(current_coin)
				elif m_multiple > 2.5:
					tweet = tweet_msg(current_coin, current_price, m_multiple)
					status = api.update_status(status=tweet)
					print "Just tweeted: " + tweet
					if current_coin not in overvalued:
						overvalued.append(current_coin)
				else:
					time.sleep(.5)
			time.sleep(.1)
		print "Currently UNDERvalued [i.e., BUY!]:"
		print undervalued
		print "\nCurrently OVERvalued [i.e., SELL!]:"
		print overvalued
		time.sleep(300)

if __name__ == "__main__":
  main()
