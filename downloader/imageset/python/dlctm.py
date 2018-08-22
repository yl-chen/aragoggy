###########################################################
##
## This program uses to download image files from *****. It
## connects the image set URL and read how many pages it has
## and then it connects every pages the image set has, down-
## load images from those pages.
##
## Requirement:
##   Python 3, BeautifulSoup, lxml
## https://www.cartoonmad.com/comic/7491.html
## Parameters: <URL of image set> <folder to store> (page number to start)
##
###########################################################

import http.client, sys, html.parser, urllib.request, random, time, ssl, os

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

# download remote resource to specified location
def dl2(resourceURL, locToSave):
	print("resourceURL>>"+resourceURL+", locToSave>>"+locToSave)
	
	req = urllib.request.Request(resourceURL, headers={'User-Agent': 'Mozilla/5.0'})
	with urllib.request.urlopen(req) as response:
		with open(locToSave, "wb") as the_file:
			the_file.write(response.read())
			
	return

# ;)
secret1 = 'cart'
secret2 = 'onmad.co'
	
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

if tarURL.endswith('.html') == False:
	print('URL not ends with .html')
	exit()

if idxSlashSlash == -1:
	print('cannot find //')
	exit()

if idxEndOfDomain == -1:
	print('cannot find domain')
	exit()

idxTmp = 0;
idxLatestSlash = -1;

while idxTmp != -1:
	idxTmp = tarURL.find('/', idxTmp + 1, len(tarURL))
	if idxTmp > idxLatestSlash:
		idxLatestSlash = idxTmp

#print('idxTmp>>'+str(idxTmp))
#print('idxLatestSlash>>'+str(idxLatestSlash))

strComicId = tarURL[idxLatestSlash+1:len(tarURL)-5]

#print('strComicId>>'+strComicId)

strProtocol = tarURL[0:idxSlashSlash].lower()
strDomain = tarURL[idxSlashSlash+3:idxEndOfDomain]

strReqLoc = tarURL[idxEndOfDomain:len(tarURL)]

#print('strReqLoc>>'+strReqLoc)

response = hget(strProtocol, "GET", strDomain, strReqLoc)

html = response.read()
print("Target connected. Under investigations...")
print('------------------------------------------------------')

# stage 1, to know each chapter's URL

idxTmp = 0
lenHTML = len(html)
strHTML = str(html)
listChapters = []

while idxTmp != -1:
	strTarHref = 'href=/comic/' + strComicId
	idxTmp2 = strHTML.find(strTarHref, idxTmp + 1, lenHTML)
	idxTmp3 = strHTML.find(strTarHref + '.html', idxTmp + 1, lenHTML)
	
	idxTmp = idxTmp2
	
	if idxTmp2 == -1:
		continue
	
	# skip if it directing to comic main page
	if idxTmp2 == idxTmp3:
		continue
	
	# take chapter URL
	idxTmp4 = strHTML.find('.html', idxTmp, lenHTML)
	
	listChapters.append(strHTML[idxTmp+5:idxTmp4+5])
	
	#print(strHTML[idxTmp:idxTmp4+5])
	
print('found number of chapters: ' + str(len(listChapters)))

try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

# take comic images from each chapters ans saving them
for chapterReqLoc in listChapters:
	print('go to chapter page ' + chapterReqLoc + '...')
		
	response = hget(strProtocol, "GET", strDomain, chapterReqLoc)
	html = response.read()
	
	#print(html)
	
	# to know each comic pages in this chapter
	soup = BeautifulSoup(html, "lxml")
	htmlSeleOptTags = soup.find_all("option", selected=False)
	
	print('number of option: ' + str(len(htmlSeleOptTags)))
	
	# create folder for the chapter
	strChapterFolderPath = tarPath + '/' + chapterReqLoc[7 + len(strComicId):len(chapterReqLoc) - 5 - 3];
	if not os.path.exists(strChapterFolderPath):
		os.makedirs(strChapterFolderPath)
	
	for optTag in htmlSeleOptTags:
		# option's value; such as 749100142022001.html
		optTagVal = str(optTag['value'])
		
		print('taking image from ' + optTagVal)
		
		response = hget(strProtocol, "GET", strDomain, '/comic/'+optTagVal)
		html = response.read()
		
		soup2 = BeautifulSoup(html, "lxml")
		htmlImgs = soup2.find_all("img")
		
		for imgTag in htmlImgs:
			imgURL = imgTag['src']
			
			# target found
			if imgURL.startswith('http://web.'+secret1+'o'+secret2+'m/') or imgURL.startswith('http://web2.'+secret1+'o'+secret2+'m/'):
				dl2(imgURL, strChapterFolderPath + '/' + imgURL[len(imgURL)-7:len(imgURL)])
				break
			
		# XXX force stop
#		if True:
#			print("[debug] force stop ======================")
#			exit()
		
		# sleep for not too aggressive
		sleepSecond = random.randint(0,2)
		time.sleep(sleepSecond);
	
print("process done")
