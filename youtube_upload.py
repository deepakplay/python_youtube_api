# -*- coding: utf-8 -*-

import os
import json
import requests
import cloudscraper
from colorama import init
from moviepy.editor import *
from html.parser import HTMLParser

length = 1
count = 0
maindata = []
WHITE = '\033[1;37m'
GREEN = '\033[0;32m'
RED = '\033[1;31m'
LRED = '\033[1;31m'

def shorturl(surl):
    response = requests.put( "https://api.shorte.st/v1/data/url",
                            {"urlToShorten":surl},
                            headers={"public-api-token": "url-shotener-token"})
    decoded_response = json.loads(response.content)
    open('shrinkurl.txt','a').write(decoded_response['shortenedUrl']+'\n')
    return decoded_response['shortenedUrl']
    
def is_downloadable(url):
    content_type = requests.head(url, allow_redirects=True).headers.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True
    
def convertvideo(vidin, vidout):
    video = VideoFileClip(vidin)
    if video.w <=500:
        fontsize = 30
    elif video.w <= 800:
        fontsize = 40
    elif video.w <=1100:
        fontsize = 60
    elif video.w >1100:
        fontsize = 70
    txt_clip = ( TextClip("Download link in the description",
                                        fontsize=fontsize,
                                        font='Proxima-Nova-Bold',
                                        color="white")
                            .set_position(("center", (video.h-200)))
                            .set_duration(video.duration)
                            .set_opacity(.75)
                    )
    result = CompositeVideoClip([video, txt_clip])
    result.write_videofile(vidout,codec='libx264')
    return
                
def fileread():
    try:
        if os.stat("maindata.txt").st_size == 0:
            raise FileNotFoundError("File is empty") 
        main_file = open("maindata.txt", 'r')
        print(GREEN +"  [*] Reading File...")
        data_read = []
        while True:
            linedata = main_file.readline()
            if not linedata:
                break
            recording = False
            data_read = []
            string = ''
            for i in linedata:
                if i == '[' or i == ',' or i == ']':
                    continue
                elif i == '\'':
                    if recording == False:
                        string = ''
                        recording = True
                    else:
                        recording = False
                        data_read.append(string)
                else:
                    string = string + i
            maindata.append(data_read)
        global count
        count = int(data_read[0])
    except FileNotFoundError:
        main_file = open("maindata.txt", 'a')
    main_file.close()
    return
    
def upload(data):
    up_file = ''
    if not is_downloadable(data[2]):
        return False
    print(GREEN +"  [*] Downloading Video ["+str(count)+"]....")
    if not os.path.exists("temp"):
        os.makedirs("temp")
    downvid = "temp/downvid.mp4"
    vidr = requests.get(data[2])
    filev = open(downvid,'wb')
    filev.write(vidr.content)
    filev.close()
    
    print(GREEN +"  [*] Editing Video....")
    editvid = "temp/editvid.mp4"
    convertvideo(downvid,editvid)
    
    print(GREEN +"  [*] Generating Upload data...")
    link2 = data[2]
    list_link1 = data[1].split('/')[2].split('-')
    short_link720 = shorturl("https://pixabay.com/videos/download/video-"+list_link1[-1]+"_medium.mp4?attachment")
    short_link1080 = shorturl("https://pixabay.com/videos/download/video-"+list_link1[-1]+"_large.mp4?attachment")
    short_linkorg = shorturl("https://pixabay.com/videos/download/video-"+list_link1[-1]+"_source.mp4?attachment")
    vidname = ' '.join(list(map(lambda st:st.capitalize(), list_link1[:-1]))) +" - Copyright Free stock video footage"
    keywords = ', '.join(list(map(lambda st:st.lower(), list_link1[:-1]))) 
    keywords = keywords + "stock, video, free, download, footage, background, copyright, youtube, hd, high, quality, professional"
    description = "Support us by Subscribe and Share\\n\\nDownload Link:\\n\t720p:\t"
    description = description + short_link720 + "\\n\t1080p:\t" + short_link1080 + "\\n\tOrginal video:\t" + short_linkorg
    description = description +"\\n\\n\\n\\nHigh quality royality free stock videos for free download from Pixabay.\\nfree for commercial use.\\nno attribution required"
    print(GREEN+"  [*] Uploading data Youtube... " + data[1])
    
    up_file = up_file + ''
    up_file = 'python upload_video.py'
    up_file = up_file + ' --file="'+editvid+'"'
    up_file = up_file + ' --title="'+vidname+'"'
    up_file = up_file + ' --description="'+description+'"'
    up_file = up_file + ' --keywords="'+keywords+'"'
    up_file = up_file + ' --category="22"'
    up_file = up_file + ' --privacyStatus="public" '
    
    os.system(up_file)
    return True

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.found = 0
        self.found1 = 0
        self.found2 = 0
        self.main_file = open("maindata.txt", 'a')
        self.data = []

    def handle_starttag(self, tag, attrs):
        
        if tag == 'a' and self.found == 1:
            for name, value in attrs:
                if name == 'href':
                    self.data.clear()
                    self.data.append('0')
                    self.data.append(value)
            self.found = 0
        
        if tag == 'input':
            for name, value in attrs:
                if name=='name' and value == 'pagi':
                    self.found1 = 1
                    break

        if tag != 'div':
            return;
        else:
            for name, value in attrs:
                if name == 'itemtype' and value == "schema.org/VideoObject":
                    self.found = 1
                elif name == 'data-mp4':
                    self.data.append("https:"+value)
                    
                    for item in maindata:
                        if item[1] == self.data[1]:
                            self.found2 = 1
                            break
                    if self.found2 == 1:
                        print('-'*80)
                        print(RED+"  Skipping..." + self.data[1])
                        self.found2 = 0
                    else:
                        global count
                        count = count + 1
                        self.data[0] = str(count)
                        print('-'*80)
                        if upload(self.data):
                            self.main_file.write(str(self.data)+'\n')
                            self.main_file.close()
                            self.main_file = open("maindata.txt", 'a')
                            print(GREEN +"  [*] Upload Successfully...")
                            input()
                        else:
                            print(LRED +"  [*] Error: Broken Link...")

    def handle_data(self, data):
        if self.found1 == 1:
            global length
            length = [int(i) for i in data.split() if i.isdigit()][0]
            self.found1 = 0

if __name__ == "__main__": 
    init(autoreset=True)
    fileread()
    cou = 1
    weblist = ['latest','upcoming','popular','ec']
    scraper = cloudscraper.create_scraper()

    for st in weblist:
        cou = 1
        while cou <= length:
            url = 'https://pixabay.com/videos/search/?order='+st+'&pagi=' + str(cou)
            print (RED +"\n  Page :" + str(cou) + " " +url+"\n")
            res = str(''.join([i if ord(i) < 128 else ' ' for i in scraper.get(url).text]))
            parser = MyHTMLParser()
            parser.feed(res)
            cou = cou+1
           
