###########################################################
##
## This program uses to download image files from *****. It
## connects the image set URL and read how many pages it has
## and then it connects every pages the image set has, down-
## load images from those pages.
##
## Requirement:
##   Python 3, Selenium
##
## Parameters: <URL of image set> <folder to store> (skip until)
##
###########################################################

import sys, urllib.request, random, time

if len(sys.argv) < 3:
	print('wrong size of inputed arguments...; size: '+str(len(sys.argv)))
	print('usage: <chapter d-m-eden url> <target folder to save> (page number that skip until it comes)')
	exit()

tarURL = sys.argv[1]
tarPath = sys.argv[2]

iSkipNum = -1
skipNum = ""
if len(sys.argv) > 3:
	skipNum = sys.argv[3]

print('Target: '+tarURL)
print('Local folder: '+tarPath)
print('Skip until: '+skipNum)
print('------------------------------------------------------')

from pathlib import Path

path = Path(tarPath)

if not path.exists():
	print('target forder not exist')
	exit()

if not path.is_dir():
	print('invalid target folder')
	exit()

if len(tarURL) == 0:
	print('root URL is empty')
	exit()

if skipNum != "":
	iSkipNum = int(skipNum)

idxSlashSlash = tarURL.find('://', 0, len(tarURL))
idxEndOfDomain = tarURL.find('/', idxSlashSlash + 3, len(tarURL))

if '.html' not in tarURL:
	print('URL not ends with .html')
	exit()

if idxSlashSlash == -1:
	print('cannot find //')
	exit()

if idxEndOfDomain == -1:
	print('cannot find domain')
	exit()

idxTmp = tarURL.find('.html')

strUrlPrefix = tarURL[0:idxTmp-1]
strUrlSuffix = tarURL[idxTmp:len(tarURL)]

# print(strUrlPrefix)
# print(strUrlSuffix)

# pre defined total of page number
pgTotal = 100
pgCurr = 1
flagPgUpdate = False
strImgFilePadding = "0000000000"

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get(strUrlPrefix+str(pgCurr)+strUrlSuffix)

while pgCurr <= pgTotal:

	if not flagPgUpdate:
		elem = driver.find_element_by_class_name("cHeader")
		elem = elem.find_element_by_tag_name("b")
		txt = elem.text
		# print("[debug] raw "+txt);

		idxTmp = txt.find('/')
		txt = txt[idxTmp+1:len(txt)].strip();
		# print("[debug] stripped "+txt);
		pgTotal = int(txt)
		flagPgUpdate = True

	if iSkipNum != -1:
		if pgCurr<iSkipNum:

			# go next page directly
			pgCurr += 1
			elem = driver.find_element_by_id("btnPageNext")
			elem.click()

			continue

	elem = driver.find_element_by_id("iBody")
	images = elem.find_elements_by_tag_name("img")

	# the 2nd is our target
	src = images[1].get_attribute('src')
	#print("[debug] src "+src);

	strPadding = strImgFilePadding[0:(5-len(str(pgCurr)))]
	tarDest = tarPath + '/' + strPadding + str(pgCurr) + ".jpg"
	#print("[debug] tarDest "+tarDest);
	urllib.request.urlretrieve(src, tarDest)

	sleepSecond = random.randint(2, 8)
	time.sleep(sleepSecond);

	# go next page
	pgCurr += 1
	elem = driver.find_element_by_id("btnPageNext")
	elem.click()

driver.close()
print("process done")
