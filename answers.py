from selenium import webdriver
import wolframalpha, duckduckgo
import urllib, urllib2, webbrowser, json
import time, datetime
import stop_words
import threading
import random
import re
import os

from bs4 import BeautifulSoup
#from nltk.tag.util import untag
#from stanfordtagger import *

def youtube_search(query):
	"""
	function responsible for retrieving
	search results from YouTube
	"""
	
	query = urllib.quote(query)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, "lxml")
	link_list = ["https://www.youtube.com/watch?v=" + id for id in 
	re.findall(r'href=\"\/watch\?v=(.{11})', html)]
	return link_list
	
def weather_search():
	"""weather function that uses wordweatheronline
	API to obtain weather information for the day"""
	
	api_key = "00b517e93bce35fd91ac80efc0528"
	url = "http://api.worldweatheronline.com/free/v2/weather.ashx?q=TQ12%202PT&format=json&num_of_days=1&key=00b517e93bce35fd91ac80efc0528"
	
	json_obj = urllib2.urlopen(url) 
	data = json.load(json_obj)
	
	answer = ""
	
	data = data["data"]["current_condition"]
	
	for lst in data:
		
		for res in lst["weatherDesc"]:
			answer += "\nThe overall weather status is: " + res["value"] + "."

		answer += "\nThe cloud coverage is currently at " + lst["cloudcover"] + "%."
		answer += "\nThe temperature is currently " + lst["FeelsLikeC"] + " Celsius."
		answer += "\nThe humidity is at " + lst["humidity"] + "%."
		answer += "\nOverall visibility is at " + lst["visibility"] + "%."

	return answer

def duckduckgo_search(string_input):
	"""
	function responsible for retrieving data
	from Wikipedia. Info returned in list
	"""
	
	answer = ""
	
	try:
		answer = duckduckgo.get_zci(string_input, urls=False, web_fallback=False)
		if answer == "Sorry, no results.":
			refined_input = stop_words.stopwrd_removal(string_input)
			answer = duckduckgo.get_zci(refined_input, urls=False, web_fallback=False)
			if answer == "Sorry, no results.":
				answer = wolfram_search(string_input)
			else:
				answer = refined_search
		
		return answer
			
	except Exception, e:
		print(e)
	
def wolfram_search(string_input):
	"""
	function responsible for retrieving data 
	from WolframAlpha. Info returned in list
	"""
	
	client = wolframalpha.Client("XQJU5P-E49AXP5V5R")		
	result_found = False
	answer = ""
	
	try:
		res = client.query(string_input)
		if res.pods:
			for pod in res.pods:
				if pod.title == "Result":
					result = pod
					if result.text:
						result_text = result.text.split("\n")
						answer = ".\n".join(result_text)
						result_found = True
						break
			
		if not result_found:
			answer  = "No results found"
	except:
		answer = "No results found"
			
	return answer
	

