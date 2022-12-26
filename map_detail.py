import requests
from bs4 import BeautifulSoup
import csv 
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options, executable_path="E:/task/scrapping/updated/New Folder/chromedriver")


fields = ['Name', 'Review Count', 'Rating', 'Address','Opening Hours','Website','Phone','Appointment Link','Covid Info Link','Google Map Link'] 

queries = [line.strip() for line in open("input.txt", 'r')]

for query in queries:
	rows=[]
	driver.get("https://www.google.com/maps/")
	inputElement = driver.find_element("id","searchboxinput")
	print(inputElement)
	inputElement.send_keys(query)
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