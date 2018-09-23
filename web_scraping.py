import numpy as np 
import pandas as pd 
import sys, requests, shutil, os
from urllib import request, error
from datetime import date, timedelta
import datetime
#https://www.kaggle.com/abinesh100/easy-download-images-in-25-lines-py3 <--Reference code
#All of radar Data extracted from "http://www.data.jma.go.jp/mscweb/data/himawari/"

class Scraper:
    def __init__(self, region, root_region_url, base_url, verbose=False):
        self.verbose = verbose
        self.region = region
        self.root_region_url = root_region_url
        self.base_url = base_url
        self.root_dir = str("./input/"+region)
        #Creating folder and subfolder given the format /input/[Region-zone]/[timestamp as date]/[IMG]
        dirs = ["./input", self.root_dir, self.root_dir+"/"+str(date.today()), self.root_dir+"/"+str(date.today()-timedelta(1))]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)
    
    def get_file_path(self, img_name):#For assigning timestamp dir to Img
        utc_time = datetime.datetime.utcnow() #utc time right now
        #extract timestamp of file name
        img_hour = img_name.split("_")[-1].split(".")[0][:2]
        img_min = img_name.split("_")[-1].split(".")[0][2:]
        img_time = datetime.datetime.utcnow()
        img_time = img_time.replace(hour=int(img_hour), minute=int(img_min), second=0, microsecond=0)
        
        if self.verbose: #for debugging
            print("UTC time right now:"+utc_time+", Img timestamp:"+img_time)
            print("UTC time > Img time stamp:"+utc_time>img_time)
            
        if utc_time > img_time: #time comparison to classify whether it is yesterday's data or today's data
            file_path = str(self.root_dir+"/"+str(date.today()))
        else:
            file_path = str(self.root_dir+"/"+str(date.today()-timedelta(1)))
        return file_path
    
    def fetch_img(self, path, file_path):
        url=path
        try:
            response=requests.get(url, stream=True)
        except requests.exceptions.ConnectionError:
            if self.verbose:
                print("Connection Abort") #INCASE OF FAILED LINK, SKIP IT. DOWNLOAD LATER
            return False
        with open(file_path+"/image.jpg", 'wb') as out_file: #download IMG as image.jpg, will change name later
            shutil.copyfileobj(response.raw, out_file)
        del response    
        return True
    
    def scraping(self):
        links = []
        req = request.Request(self.root_region_url)
        with request.urlopen(req) as response:
            html = response.read().decode("utf-8")#extract all imgs link from html
            for un_slice_url in html.split("<a href=")[1:]:
                links.append(self.base_url + un_slice_url.split(">")[0])#fill extrated links into an array
        
        #for every picture links
        for link in links:
            #extract image name from url
            #Example: http://www.data.jma.go.jp/mscweb/data/himawari/img/se1/se1_b13_0000.jpg
            #will extract se1_b13_000.jpg from url above
            img_name = link.split("/")[-1]
            file_path = self.get_file_path(img_name)#to verify timestamp directory of this picture
            
            if self.verbose:
                print("File path:"+file_path+"/"+img_name)
                
            if os.path.exists(file_path+'/'+img_name):#incase of download existing file
                if self.verbose:
                    print("File Exists")
                continue
            if self.fetch_img(link, file_path): #if Connection is success
                if self.verbose:
                    print("Connection success!")
                    
                os.rename(file_path+'/image.jpg', file_path+'/'+ img_name) 
                #rename image.jpg into image format name
                #Example:se1_b13_0000.jpg
                #This format is AREA:BAND_TYPE:TIMESTAMP.jpg
                

if __name__ == "__main__":
    #basic url of an image is "http://www.data.jma.go.jp/mscweb/data/himawari/img/[AREA]/[AREA]_[BAND_TYPE]_[TIME_STAMP].jpg"
    #so base url is "http://www.data.jma.go.jp/mscweb/data/himawari/"
    #base url will be added with additional url to download specific image
    #root_region_url basic form is "http://www.data.jma.go.jp/mscweb/data/himawari/list_[AREA].html"
    #You need to extract image's link from HTML of root_region_url to get all images_url of specific AREA.
    HA1 = Scraper(region = "ha1", 
                  root_region_url = "http://www.data.jma.go.jp/mscweb/data/himawari/list_ha1.html", 
                  base_url = "http://www.data.jma.go.jp/mscweb/data/himawari/",
                  verbose = False)
    SE1 = Scraper(region = "se1",
                 root_region_url = "http://www.data.jma.go.jp/mscweb/data/himawari/list_se1.html",
                 base_url = "http://www.data.jma.go.jp/mscweb/data/himawari/",
                 verbose = False)
    #can set vebose = True for debugging
    #to scrape use ScraperObj.scraping()
    HA1.scraping()
    #SE1.scraping()