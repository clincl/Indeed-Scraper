import csv
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
# https://www.indeed.com/jobs?q={search+query}&l={location}&start={10/1000}

# Functions:
# Get inputs
# One for all
# One per page
# One per job
# One per parameter

indeed = "https://www.indeed.com/jobs?q="

"""
Returns search & location inputs
"""
def get_params():
    search = input("Enter your indeed search: ").replace(' ','+')
    location = input("Enter your location: ")
    location = ("") if (location == "") else (location.replace(' ','+'))
    return (search, location)    
"""
Input:
params: get_params() (tuple)
page_num: (int)
Returns search page url
"""
def get_page_url(params,page_num):
    url = ""
    search = params[0]
    location = params[1]
    page_num = str(page_num * 10)
    if location == "":
        url = "https://www.indeed.com/jobs?q={search}&start={page_num}".format(search = search, page_num=page_num)
        
    else:
        url = "https://www.indeed.com/jobs?q={search}&l={location}&start={page_num}".format(search = search, location = location, page_num=page_num)
    return url
"""
url: search page url
Returns soup from  search page url
"""
def get_soup(url):
    url = requests.get(url).text
    soup = BeautifulSoup(url, 'lxml')
    return soup
"""
url: search page url
Returns list of length (max: 15) containing jobs
"""
def get_page_jobs(soup):
    #print(soup.prettify())
    jobs = soup.find_all('div', class_='jobsearch-SerpJobCard')
    return jobs

"""
page_str: 'Page x of y jobs.' string
Returns x,y
"""
def page_cap_parser(page_str):
    page_str = page_str.strip()
    page_str = page_str[5:] #Parse out "Page "
    x = y = c = 0
    for char in page_str:
        c += 1
        try:
            x *= 10
            x += int(char)
        except:
            x //= 10
            break
    page_str = page_str[c + 3:] # c + "of " = c + 3
    for char in page_str:
        try:
            y *= 10
            y += int(char)
        except:
            y //= 10
            if char == ',':
                continue
            else:
                break
    return x,y
            
"""
url: search page url
Calls page_cap_parser(page_str)
Returns total number of pages counting from 0
"""
def get_page_cap(soup):
    pages = soup.find(id="searchCountPages")
    if pages == None:
        "No \"searchCountPages\" found. One or less pages.\n Ending program.\n"
        return 0
    else:
        pages = pages.get_text()
        page_cap = ((page_cap_parser(pages)[1]//15))
        return page_cap
    
# Functions use job index in a a page
def get_job_url(job):
    job_url = job.h2.a['href']
    if job_url == None:
        return ""
    else:
        # print(job_url)
        return "https://indeed.com" +job_url
"""
url: job listing url
Returns original job application website
i.e. lever/greenhouse/myworkday/url if None
"""
def get_orig_job_url(url):
    soup = get_soup(url)
    job_site = ""
    # Check for redirect link
    job_site = soup.find(id ="originalJobLinkContainer")
    # Verify no redirect link (Apply directly on Indeed)
    if job_site == None:
        # print("No Url", url)
        return "No Url"
    else:
        a_tags = job_site.find_all('a')
        if a_tags != []:
            return a_tags[0]['href']
            # Too many requests made if original url is used.
            # But original url is needed to parse csv for url_type.
            r = requests.get(a_tags[0]['href']).url
            # # print(r.url)
            return r
        else:
            # print("FAILED",url)
            return "FAILED"
"""
url: orig_url
Parse url string to determine other(0) lever(1), greenhouse(2), myworkday(3)
Return url type
"""
# Doesn't work unless get_orig_job_url(url) sends a request
def get_url_type(url):
    if "lever.co" in url:
        return "Lever"
    elif "greenhouse.io" in url:
        return "Greenhouse"
    elif "myworkdayjobs.com" in url:
        return "Myworkdayjob"
    else:
        return "Other"
"""
Functions parsed from job search url
"""
def get_job_title(job):
    job_title = job.h2.a['title']
    if job_title == None:
        return ""
    else:
        return job_title
def get_job_company(job):
    sjcl = job.find(class_="sjcl")
    if sjcl == None:
        return ""
    else:
        company = sjcl.div.span
        return company.get_text()

def get_job_location(job):
    loc = job.find(class_="location accessible-contrast-color-location")
    if loc == None:
        return ""
    else:
        return loc.get_text()
def get_job_salary(job):
    salary = job.find(class_="salaryText")
    if salary == None:
        return ""
    else:
        return salary.get_text()
def get_job_desc(job):
    summary = job.find(class_="summary")
    if summary == None:
        return ""
    else:
        try:
            summary = summary.ul.find_all('li')  
        except:
            return summary          
        return summary

# Outputs to csv
def output_jobs(params, num_pages):
    # Encode to utf-8 to avoid UnicodeEncodeErrors
    # Name the file based on the search query and current time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S").replace(':','')
    csv_file_name = params[0] + current_time+'.csv'
    csv_file = open(csv_file_name, 'w+', encoding='utf-8', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['num','url','orig_url','url_type','title','company','location','salary','description'])
    counter = 0
    page_holder = ""
    page_cap = 99
    for page_num in range(num_pages):
        page_url = get_page_url(params, page_num)
        soup = get_soup(page_url)
        if page_num == 0:
            page_cap = get_page_cap(soup) if get_page_cap(soup) < 100 else page_cap
            print("PAGE_CAP: ", page_cap + 1, "(ORIGINAL CAP: ", get_page_cap(soup) + 1, ")")
        if page_num > page_cap:
            break
        print("Writing page: ", page_num + 1)
        page_jobs = get_page_jobs(soup)
        for job in page_jobs:
            counter += 1
            url = get_job_url(job)
            orig_url = get_orig_job_url(url)
            url_type = get_url_type(orig_url)
            title = get_job_title(job)
            company = get_job_company(job)
            location = get_job_location(job)
            salary = get_job_salary(job)
            description = get_job_desc(job)
            # print([counter,url,title,company,location,salary,description])
            csv_writer.writerow([counter,url,orig_url,url_type,title,company,location,salary,description])
    csv_file.close()
    
def main():
    # params = get_params()
    # url = get_page_url(params, 0)
    # jobs = get_page_jobs(url) # length 15 max
    # print(get_job_url(jobs[0]))
    # print(get_job_title(jobs[0]))
    # print(get_job_company(jobs[0]))
    # print(get_job_location(jobs[0]))
    # print(get_job_salary(jobs[0]))
    # print(get_job_desc(jobs[0]))

    # A. Terminal will ask for params
    # You can commment the below code and fill in the variables for B
    num_pages = input("Enter number of pages to scrap (Default 100): ")
    try:
        num_pages = int(num_pages) if (int(num_pages) >= 0 and int(num_pages) <= 100) else 100
    except:
        num_pages = 100
    params = get_params()
    
    # B. Alternatively, fill in params here so you don't need to be asked for every search
    # num_pages = 100
    # params = ("software+engineering","New+York")
    
    print("Compiling jobs into csv file...\n")
    output_jobs(params, num_pages)
    print("Finished creating csv file with job listings.\n")

if __name__ == "__main__":
    main()
