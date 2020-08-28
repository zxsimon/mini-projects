# simple script to retrieve US futures trading strategy papers with Sharpe ratios
# requires scihub API https://github.com/zaytoun/scihub.py

from scihub import SciHub
import PyPDF2
import requests
from bs4 import BeautifulSoup
import os

pub_year_onwards = "2016"
query = "Futures%20Intraday%20Strategy"

def get_paper_urls(query, page_range = (0,10), pub_year_onwards = "2016"):
    # retrieves paper URLs from Google Scholar searches
    # returns list of urls as strings
    urls = []
    for page_no in range(page_range[0], page_range[1]):
        url = 'https://scholar.google.com/scholar?as_ylo=' + \
         str(pub_year_onwards) + '&q=' + query + '&start=' + \
         str(page_no * 10) +  '&ie=UTF-8&oe=UTF-8&hl=en&btnG=Search'
        content = requests.get(url).text
        page = BeautifulSoup(content, 'lxml')
        for entry in page.find_all("h3", attrs={"class": "gs_rt"}):
            if entry.a:
                urls.append(entry.a['href'])
    return urls

def retrieve_papers(urls):
    # downloads papers based on URLs and saves them to folder based on keyword criteria
    sh = SciHub()
    papers_reviewed = 0
    # keywords for US market
    us_strings = ["S&P", "CME", "NYMEX", "NYSE",
                  "NYCE", "U.S.", "COMEX", "ICE", "CBOT"]

    for index, url in enumerate(urls):
        filename = 'paper' + str(index) + '.pdf'
        try:
            result = sh.download(url, path=filename)
        except:
            continue
        if not os.path.exists(filename):
            continue
        pdfFileObj = open(filename, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        sharpe = False
        futures = False
        us = False
        valid = False
        for page in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(page)
            page_text = pageObj.extractText()
            if not sharpe:
                if "sharpe" in page_text:
                    sharpe = True
            if not futures:
                if "futures" in page_text:
                    futures = True
            if not us:
                for string in us_strings:
                    if string in page_text:
                        us = True
            if sharpe and futures and us:
                valid = True
                break
        pdfFileObj.close()
        papers_reviewed += 1
        if not valid:
            os.remove(filename)
        print(str(index) + '/' + str(len(urls)))

    print(str(papers_reviewed) + ' papers reviewed.')

urls = get_paper_urls(query)
retrieve_papers(urls)
