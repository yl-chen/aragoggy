###########################################################
##
## This program uses to download image files from *****. It
## connects the image set URL and read how many pages it has
## and then it connects every pages the image set has, down-
## load images from those pages.
##
## Requirement:
##   Python 3, BeautifulSoup, lxml
##
## Parameters: <URL of image set> <folder to store> (page number to start)
##
###########################################################

import http.client, sys, html.parser, urllib.request, random, time

# get resource via HTTP/HTTPS
def hget(strProtocol, strMethod, strDomain, strPath):
	if strProtocol == 'http':
		httpConn = http.client.HTTPConnection(strDomain)
	elif strProtocol == 'https':
		httpConn = http.client.HTTPSConnection(strDomain)
	else:
		print('unknow protocol: '+strProtocol)
		exit()

	httpConn.request(strMethod, strPath)
	response = httpConn.getresponse()
	if response.status != 200:
		print("http " + strMethod + " failed on " + strPath + " with status " + str(response.status))
		exit()
		
	return response

if len(sys.argv) < 3:
	print('wrong size of inputed arguments...; size: '+str(len(sys.argv)))
	print('usage: <root url> <target folder to save> (page number that skip until it comes)')
	exit()

tarURL = sys.argv[1]
tarPath = sys.argv[2]

skipNum = ""
if len(sys.argv) > 3:
	skipNum = sys.argv[3]

print('Target: '+tarURL)
print('Local folder: '+tarPath)
print('Skip until: '+skipNum)
print('------------------------------------------------------')
	
from pathlib import Path
path = Path(tarPath)

if False == path.exists():
	print('target forder not exist')
	exit()

if False == path.is_dir():
	print('invalid target forder')
	exit()

if len(tarURL) == 0:
	print('root URL is empty')
	exit()
	
if skipNum != "":
	int(skipNum)
	
idxSlashSlash = tarURL.find('://', 0, len(tarURL))
idxEndOfDomain = tarURL.find('/', idxSlashSlash+3, len(tarURL))

if idxSlashSlash == -1:
	print('cannot find //')
	exit()

if idxEndOfDomain == -1:
	print('cannot find domain')
	exit()

strProtocol = tarURL[0:idxSlashSlash].lower()
strDomain = tarURL[idxSlashSlash+3:idxEndOfDomain]

if tarURL.endswith('/1'):
	strReqLoc = tarURL[idxEndOfDomain:len(tarURL)-1]
else:
	strReqLoc = tarURL[idxEndOfDomain:len(tarURL)]

#print('>>'+strReqLoc)

response = hget(strProtocol, "GET", strDomain, strReqLoc + '/1')

html = response.read()
print("Target connected. Under investigations...")
print('------------------------------------------------------')

try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "lxml")

# get number of pages
if len(soup.find_all("select")) != 1:
	print('invalid length of <select> to parse')
	exit()

htmlSeleOptTags = soup.find_all("select")[0].find_all("option")

# check each page
for htmlOption in htmlSeleOptTags:
	htmlOptVal = str(htmlOption['value'])
	
	# [DEBUG] to stop the script
#	if htmlOptVal == '3':
#		print('stop for debugging')
#		exit()

	if skipNum != "":
		if int(htmlOptVal) < int(skipNum):
			continue
	
	sleepSecond = random.randint(0,2)
	time.sleep(sleepSecond);
		
	imgPageURL = strReqLoc + htmlOptVal
	print("process... " + strProtocol + "://" + strDomain + imgPageURL)
	
	response = hget(strProtocol, "GET", strDomain, imgPageURL)

	html = response.read()
	
#	print(html)
#	print('==========================')
	
	soup2 = BeautifulSoup(html, "lxml")
	foundImgTag = soup2.find(id="defualtPagePic")
	
	if foundImgTag == None:
		print("ignore page " + htmlOptVal)
		continue
	
	imgURL = str(foundImgTag['src'])
	print("img>>"+imgURL)
	
	req = urllib.request.Request(imgURL, headers={'User-Agent': 'Mozilla/5.0'})
	with urllib.request.urlopen(req) as response:
		paddedZeros = 4 - len(htmlOptVal)
		
		if paddedZeros < 0:
			paddedZeros = 4
		
		padding = ""
		for x in range(paddedZeros):
			padding += "0"
		
		with open(tarPath + "/" + padding + htmlOptVal + ".jpg", "wb") as the_file:
			the_file.write(response.read())
	
print("process done")
