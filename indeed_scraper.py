import csv
import requests
from bs4 import BeautifulSoup
import config
#Indeed increments its pages every 10 for the start param
# pg0=0 pg2=10 ...
#EXAMPLE: "https://www.indeed.com/jobs?q=technology+summer+internship+2020&jt=internship&start=20"
#So we can format our url like so:
# https://www.indeed.com/jobs?q=
# technology+summer+internship+2020
# &jt=internship&explvl=entry_level
# &start=
# 20

indeed = "https://www.indeed.com/jobs?q="

#search = config.search
#search = "summer intern"
search = input("Enter your indeed search: ")

search = search.replace(' ','+')

# TODO: Need to change params to dict format for requests.get() argument.

#params = "&l=United+States&jt=internship&explvl=entry_level&start="
params = "&l=United+States&start="
page = 0

url = indeed + search + params + str(page)
print(url)
url = requests.get(url).text

#CSV
csv_file = open('indeed_scrape.csv','w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['counter','title','company','location','url'])
#BS4
soup = BeautifulSoup(url, 'lxml')
#print(soup.prettify())
jobs = soup.find_all('div', class_='jobsearch-SerpJobCard')
#print(jobs)
#Searches cap at 990
counter = 0
while(page<1000):
    for job in jobs:
        counter += 1
        #TITLE
        try:
            title = job.div.a['title']
            #print(title)
        except:
            title = ""
            pass
        #COMPANY
        try:
            company = job.find('div', class_='sjcl').div.span.a.contents[0][9:]
            #print(company)
        except:
            company = ""
            pass
        # rating = job.find('div',class_='sjcl')
        #print(rating)
        # Had difficulties parsing rating but I don't care about the rating anyway.
        #LOCATION    
        try:
            location = job.find('div', class_='location').contents[0]
            #print(location)
        except:
            location = ""
            pass
        #URL
        try:
            url = "http://indeed.com" + job.div.a['href']
            #print(url)
        except:
            url = ""
            pass
        try:
            csv_writer.writerow([counter,title,company,location,url])
        except:
            pass
    #NEXT PAGE
    page += 10
    url = indeed + search + params + str(page)
    url = requests.get(url).text
    soup = BeautifulSoup(url, 'lxml')
    jobs = soup.find_all('div', class_='jobsearch-SerpJobCard')
csv_file.close()
