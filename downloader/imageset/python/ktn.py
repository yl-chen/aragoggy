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
## Parameters: <URL of image set> <folder to store>
##
###########################################################

import http.client, sys, html.parser, urllib.request, random, time

# get resource via HTTP/HTTPS
def hget(strProtocol, strMethod, strDomain, strPath):
	if strProtocol == 'http':
		httpConn = http.client.HTTPConnection(strDomain)
	elif strProtocol == 'https':
		httpConn = http.client.HTTPSConnection(strDomain)
		return httpConn
	else:
		print('unknow protocol: '+strProtocol)
		exit()

	httpConn.request(strMethod, strPath)
	response = httpConn.getresponse()
	if response.status != 200:
		print("http " + strMethod + " failed on " + strPath)
		exit()
		
	return response

if len(sys.argv) !=3:
	print('wrong size of inputed arguments...; size: '+str(len(sys.argv)))
	print('usage: <root url> <target folder to save>')
	exit()

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

print('Target: '+tarURL)
print('Local folder: '+tarPath)
print('------------------------------------------------------')
	
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
print('')

try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "lxml")

# img.all_attrs
#print("a >> "+ str(soup.find(id="defualtPagePic").attrs))
# img.src
#print("b >> "+ str(soup.find(id="defualtPagePic")['src']))
#print("c >> "+ str(soup.find_all("select")))

if len(soup.find_all("select")) != 1:
	print('invalid length of <select> to parse')
	exit()

htmlSeleOptTags = soup.find_all("select")[0].find_all("option")

for htmlOption in htmlSeleOptTags:
	htmlOptVal = str(htmlOption['value'])
	if htmlOptVal == '3':
		print('stop for debugging')
		exit()
	
	sleepSecond = random.randint(0,2)
	time.sleep(sleepSecond);
		
	imgPageURL = strReqLoc + htmlOptVal
	print("process... " + strProtocol + "://" + strDomain + imgPageURL)
	
	response = hget(strProtocol, "GET", strDomain, imgPageURL)

	html = response.read()
	
#	print(html)
#	print('==========================')
	
	soup2 = BeautifulSoup(html, "lxml")
	
	imgURL = str(soup2.find(id="defualtPagePic")['src'])
	print("img>>"+imgURL)
	
	req = urllib.request.Request(imgURL, headers={'User-Agent': 'Mozilla/5.0'})
	with urllib.request.urlopen(req) as response:
		with open(tarPath + "/" + htmlOptVal + ".jpg", "wb") as the_file:
			the_file.write(response.read())
	
print("process done")
