'''
Created on May 30, 2014

@author: Wasif Sikder
@version: Python 3.0+

For every name in the given name-list.txt file, downloads <=32 images for frontal pose,
<=120 images for profile pose, and keeps a list of their URLs in image-urls.txt file
'''

import os, json, re, time, random, urllib2
from urllib import FancyURLopener

# Initialize URLopener object
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
myopener = MyOpener()


def downloadImages(searchTerm, numImages, folder, startCount, imageName):
    '''
    Downloads given number of images for given search term to given folder
    Appends URL of each image to universal image-urls.txt file

    @requires: Search term string
    @requires: Number of images to download.
    @requires: Folder string to place image
    @requires: The count of the first image
    @requires: Name to save image as

    @attention: 8 < numImages < 60. > 60 creates infinite loop
    @attention: numImages % 8 should = 0, (else truncated)
    @attention: Must not have odd characters in name-list.txt
                e.g. Second e in Rene Descartes can't have accent
    '''

    count = startCount

    # Append search term name to URLs text file
    if count == 0:
        with open('image-urls.txt', mode='a') as urlfile:
            urlfile.write('\n' + imageName + '\n')
        with open('currenturls.txt', mode='w') as curr:
            curr.truncate()

    # Replace search term spaces with '%20' for request
    searchTerm = searchTerm.replace(' ', '%20')

    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Retrieve eight images in each loop using Google Images API
    i = 0
    while i < (numImages/8):


        # Set options for search results allowed, and create request
        # Current options:
            # Send random user IP with request
            # Only face images
            # Minimum size is small (no icons)
            # 8 Results per return
        ipstarts = [3,4,6,7,8,9,11,12,13,15,16,17,18,19,20,21,22,23,24,26,28,29,30,32,33,34,35,38,40,44,45,48,50,52,54,55,56,63,73,214,215]
        randip = str(random.choice(ipstarts)) + '.' + '.'.join('%s'%random.randint(0, 255) for i in range(3))
        options = '&userip='+randip+'&imgtype=face&imgsz=small|medium|large|xlarge&rsz=8'

        url = ('https://ajax.googleapis.com/ajax/services/search/images?'+'v=1.0&q='+searchTerm+options+'&start='+str(i*8))
        print(url) # Print formed URL for debug


        # Get API source
        try:
            req = urllib2.Request(url, None, {'Referer': 'http://www.umiacs.umd.edu/research'})
            data = urllib2.urlopen(req).read();
        except (KeyboardInterrupt, SystemExit): raise
        except:
            time.sleep(random.uniform(1,4))
            continue # Sleep and retry if API retrieval fails


        # Get image data from API source using JSON
        results = json.loads(data.decode('utf8'))
        if results: data = results['responseData']
        else: continue
        if data: dataInfo = data['results']
        else:
            time.sleep(random.uniform(1,4))
            continue # Retry if parsing fails

        # retry if failed (i won't increase), else increase i
        i = i + 1

        # Iterate through each URL
        for myUrl in dataInfo:
            url = myUrl['unescapedUrl']

            # Get redirected URL if needed
            st = re.findall('\.jpg$|\.jpeg$|\.png$|\.gif$|\.bmp$|\.svg$|\.ico$|\.webp$',url)
            if not st:
                try:
                    req = urllib2.Request(url)
                    res = urllib2.urlopen(req)
                    url = res.geturl()
                except (KeyboardInterrupt, SystemExit): raise
                except: pass # Use original URL if fail

            print(url) # for debug

            # If URL not downloaded already (not in file), download it
            with open('currenturls.txt', mode='r') as curr:
                if any(url == x.rstrip('\r\n') for x in curr):
                    time.sleep(random.uniform(0,1))
                    continue # skip if already downloaded

            # Download image to specified folder as (count).(suffix)
            s = re.findall('\.[a-zA-Z0-9_]{0,}$',url)
            if s: suffix =  s[len(s)-1]
            else:
                time.sleep(random.uniform(0,1))
                continue # If suffix finding failed, skip

            # Filename forming fails if odd chars in name-list.txt
            # e.g. If second e in Rene Descartes has an accent
            try:
                count = count + 1
                filename = imageName + ' ' + str(count)
                filename = filename.replace(' ', '_') + suffix
            except (KeyboardInterrupt, SystemExit): raise
            except:
                count = count - 1
                time.sleep(random.uniform(0,1))
                continue # If filename forming failed, skip

            print(filename) # for debug

            try:
                myopener.retrieve(url, folder + filename)
            except (KeyboardInterrupt, SystemExit): raise
            except:
                count = count - 1
                time.sleep(random.uniform(0,1))
                continue # If image download failed, skip

            # Will only get here if image downloaded successfully
            # Append URL and its count to text file and current urls
            with open('image-urls.txt', mode='a') as logfile:
                logfile.write(str(count) + ': ' + url + '\n')

            with open('currenturls.txt', mode='a') as curr:
                curr.write(url + '\n')

            # Sleep for a second to keep Google happy
            time.sleep(random.uniform(0,1.5))

    # return total successful after everything finished
    return count




if __name__ == '__main__':
    '''
    Main method calls downloadImages for both poses for all names in text file
    '''
    with open('name-list.txt') as namefile:
        for line in namefile:
            name = line.strip()
            downloadImages(name, 32, 'dataset/' + name + '/frontal/', 0, name+' Frontal')
            # Using three search terms, profile, side and turned, 56 is max dl size
            currentCount = downloadImages(name + ' Profile', 56, 'dataset/' + name + '/profile/', 0, name+' Profile')
            currentCount2 = downloadImages(name + ' Side', 56, 'dataset/' + name + '/profile/', currentCount, name+' Profile')
            downloadImages(name + ' Turned', 56, 'dataset/' + name + '/profile/', currentCount2, name+' Profile')