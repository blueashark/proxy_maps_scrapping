import requests
from bs4 import BeautifulSoup
import csv 
import time
import mysql.connector
import numpy
from lxml.html import fromstring
from itertools import cycle

from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import traceback
def get_proxies():
	url = 'https://free-proxy-list.net/'
	response = requests.get(url)
	parser = fromstring(response.text)
	proxies = set()
	for i in parser.xpath('//tbody/tr'):
		if i.xpath('.//td[7][contains(text(),"yes")]'):
			proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
			proxies.add(proxy)
	return proxies
#If you are copy pasting proxy ips, put in the list below
#proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']
proxies = get_proxies()
proxy_pool = cycle(proxies)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
)
mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS scrapeddata")
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="scrapeddata"
)
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS data ( id int AUTO_INCREMENT PRIMARY KEY, name text, review_count text, rating text, address text, opening_hours text, website text, phone text, appointment text, covid_info text, map_link text, detais text)")






fields = ['Name', 'Review Count', 'Rating', 'Address','Opening Hours','Website','Phone','Appointment Link','Covid Info Link','Google Map Link',"details"] 

dest = [line.strip() for line in open("input.txt", 'r')]
category="dentist in "

for query in dest:
	rows=[]
	driver=None
	for i in range(1,11):
		#Get a proxy from the pool
		proxy = next(proxy_pool)
		print(proxy)
		print("Request #%d"%i)
		options = Options()
		options.headless = True
		options.add_argument("--window-size=1920,1200")
		# options.add_argument('--proxy-server=http://%s' % proxy)

		driver = webdriver.Chrome(options=options, executable_path="E:/task/scrapping/updated/chromedriver")
		error=0
		try:
			driver.get("https://www.google.com/maps/")
		except:
			error=1
		if error==1:
			continue
		else:
			print("SUCCESSS")
			break

	inputElement = driver.find_element("id","searchboxinput")
	inputElement.send_keys(category+query)
	inputElement.send_keys(Keys.RETURN)
	time.sleep(5)
	source=""
	scroll=driver.find_element('xpath','//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
	while True:
		if "You've reached the end of the list." in driver.page_source:
			source=driver.page_source
			break
		scroll.send_keys(Keys.PAGE_DOWN)

	data=source

	soup = BeautifulSoup(data, 'html.parser')
	all_links=soup.find_all("a",{"class": "hfpxzc"})
	urls=[]

	for link in all_links:
		urls.append(link['href'])


	for url in urls:
		#driver.get("https://www.google.com/maps/place/Treehouse+Dental+Care+-+Toronto/data=!4m7!3m6!1s0x882b3344e7eb72d5:0x893abc612b2f7df4!8m2!3d43.6894573!4d-79.3950643!16s%2Fg%2F11cjxf81rd!19sChIJ1XLr50QzK4gR9H0vK2G8Ook?authuser=0&hl=en&rclk=1")
		driver.get(url)
		data=driver.page_source
		soup = BeautifulSoup(data, 'html.parser')


		name=""
		review_count=""
		rating=""
		address=""
		hours=""
		appointment=""
		website=""
		phone=""
		covid_link=""

		review_rating=soup.find("div",{"jsaction":"pane.rating.moreReviews"})

		if soup.find("h1",{"class":"DUwDvf fontHeadlineLarge"}):
			name=soup.find("h1",{"class":"DUwDvf fontHeadlineLarge"}).text.strip()
		if review_rating and review_rating.find("span",{"style":"color:#1A73E8"}):
			review_count=review_rating.find("span",{"style":"color:#1A73E8"}).text.strip()
		if review_rating and review_rating.find("span",{"class":"ceNzKf"}):
			rating=review_rating.find("span",{"class":"ceNzKf"})['aria-label']
		if soup.find("button",{"data-item-id":"address"}):
			address=soup.find("button",{"data-item-id":"address"}).text.strip()
		if soup.find("table",{"class":"eK4R0e fontBodyMedium"}):
			hours=soup.find("table",{"class":"eK4R0e fontBodyMedium"}).text.strip()
		if soup.find("a",{"data-item-id":"action:3"}):
			appointment=soup.find("a",{"data-item-id":"action:3"}).text.strip()
		if soup.find("a",{"data-item-id":"authority"}):
			website=soup.find("a",{"data-item-id":"authority"}).text.strip()
		if soup.find("button",{"data-tooltip":"Copy phone number"}):
			phone=soup.find("button",{"data-tooltip":"Copy phone number"}).text.strip()
		if soup.find("a",{"data-tooltip":"Open COVID-19 info link"}):
			covid_link=soup.find("a",{"data-tooltip":"Open COVID-19 info link"})
			covid_link=covid_link["href"]
		sql = "INSERT INTO data (name, review_count,rating,address,opening_hours,website,phone,appointment,covid_info,map_link) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)"
		val = (name,review_count,rating,address,hours,website,phone,appointment,covid_link,url)
		mycursor.execute(sql, val)
		mydb.commit()
		if soup.find("div",{"class":"y0K5Df"}):
			ele=soup.find("div",{"class":"y0K5Df"})
			ele.click()
			data=driver.page_source
			soup_v = BeautifulSoup(data, 'html.parser')
			details=[]
			possiblities=soup_v.find_all("li",{"class":"hpLkke"})
			for possibility in possiblities:
				if"WeoVJe" in possibility.get_Attribute("class").split():
					name=possibility.find("span").text.strip()
					details.append({"name":name,"val":0})
				else:
					name=possibility.find("span").text.strip()
					details.append({"name":name,"val":1})
			sql="INSERT INTO data(details) VALUES (%s)"
			val=(details)
			mycursor.execute(sql, val)
			mydb.commit()
		rows.append([name,review_count,rating,address,hours,website,phone,appointment,covid_link,url])

		#break

	with open((query+".csv"), 'w') as csvfile: 
	    # creating a csv writer object 
	    csvwriter = csv.writer(csvfile) 
	        
	    # writing the fields 
	    csvwriter.writerow(fields) 
	        
	    # writing the data rows 
	    csvwriter.writerows(rows)

'''
print(name)
print(review_count)
print(rating)
print(address)
print(hours)
print(appointment)
print(website)
print(phone)
print(covid_link["href"])
'''

driver.quit()

'''
page_url="https://www.google.com/maps/place/Downtown+Dental+Clinic/data=!4m7!3m6!1s0x882b34aeb871023b:0x57ffa1dad064b51e!8m2!3d43.6726771!4d-79.387355!16s%2Fg%2F11df43ws2q!19sChIJOwJxuK40K4gRHrVk0Nqh_1c?authuser=0&hl=en&rclk=1"
data = requests.get(page_url)

soup = BeautifulSoup(data.text, 'html.parser')

print(soup)
name=soup.find_all("span",{"jstcache":"59"})
#print(name)

'''