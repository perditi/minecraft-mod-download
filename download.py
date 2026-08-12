import argparse, time, re, sys
from pathlib import Path
from os import listdir
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import os
from urllib3.exceptions import ProtocolError

# ty https://stackoverflow.com/questions/56950987/download-file-from-url-and-save-it-in-a-folder-python 
def download(dl_url: str, dest_folder: str):
    filename = dl_url.split('/')[-1].split('?mr_download_reason=standalone')[0].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(dl_url, stream=True)
    if r.ok:
        print("saving to", file_path)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))
        return False
    return True



parser = argparse.ArgumentParser(
    description='Downloads a list of Minecraft mods from Modrinth from a given .txt'
    )
parser.add_argument('filename',
                    type=str,
                    help='.txt file with one Modrinth link per line, commented lines should be preceded with \'#\''
                    )
parser.add_argument('ver',
                    help='minecraft version'
                    )
parser.add_argument('-ml', '--modloader', 
                    choices=['fabric', 'forge', 'quilt', 'neoforge'],
                    help='modloader'
                    )

args = parser.parse_args()
args.filename = args.filename.strip() # trim to acct for whitespace
args.ver = args.ver.strip()

# is the filename a file with a .txt extension? and other bs, i asked chat for this
EXT_PATTERN = re.compile(r'^(?!CON$|PRN$|AUX$|NUL$|COM[1-9]$|LPT[1-9]$)[\w,\s\-.]+\.(?i:txt)$')
if not(bool(EXT_PATTERN.match(args.filename))):
    raise Exception("Invalid file")
# is the version in the right format (i.e. 1.21.9, 1.8, 1.7.3, etc.) FIXED TO ACCOUNT FOR (26.1.4) formatting and i didn't use chat this time either biiitch
# shoutouts https://regex101.com/
VER_PATTERN = re.compile(r'^(1\.([1-9]\d?)(\.[1-9]\d*)?)|(([2-9]\d\.)([1-9]\d?)(\.[1-9]\d*)?)$')
if not(bool(VER_PATTERN.match(args.ver))):
    raise Exception("Invalid Minecraft version")

# defaults to fabric unless otherwise specificed
if args.modloader == None:
    args.modloader = 'fabric'

# directory in which to download
modsdir = Path.cwd() / f"mods({args.ver})"
Path(modsdir).mkdir(exist_ok=True) # makes the directory if it doesn't already exist

options = webdriver.EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#options.add_argument("--ignore-certificate-error")
#options.add_argument("--ignore-ssl-errors")
browser = webdriver.Edge(options=options) # we still gotta fucking use selenium bc the page needs to load otherwise we can't get shit
failed_downloads = [] # keep track of failed downloads

with open(args.filename, 'r') as file:
    for raw_url in file: # go thru all the urls in the file line by line
        raw_url = raw_url.strip() # whtiespace
        if raw_url[0:1] == '#' or raw_url == '':
            continue # skip commented + empty lines
        url = raw_url + "/versions?g=" + args.ver + "&l=" + args.modloader # go to downloads page for specific version and loader
        print(url)

        try: # why did putting this in a try catch fix this...??
            # open new tab and go to url
            print("in first try")
            browser.get(url)
            print("checkpt 3")
        except ProtocolError as pe:
            # uhhh this happens every now and again and it's bad. i don't know what to do about it though.
            print("AHHHHHH I'M DYING AGAINNNNNNNNN")
        except BaseException as e:
            print("ohhh, we're like DEAD dead thius time")
            print(type(e))
            sys.exit(1)
        finally:
            print("we in the finally up in this bihhh")
            html_source = browser.page_source
            soup = BeautifulSoup(html_source,'html.parser')
            
            try: 
                print("in second try")
                # hyperspecific navigation on modrinth webpage to find the first download link provided
                finding = soup.find('div',{'class':'normal-page__content'}).contents[1].contents[3].contents[1].contents[0].contents[2].contents[1].contents[-1].contents[0].contents[0]
                link = finding.get('href')
                print(link)
                if not download(link, modsdir):
                    raise MemoryError # i just chose this for the catch. this happens when the download no worky
            except IndexError:
                failed_downloads.append(raw_url)
                print(f"{raw_url} not available for {args.ver}")
            except MemoryError:
                failed_downloads.append(raw_url)
                print(f"{raw_url} for {args.ver} download failed")
browser.quit()
        
# save failed downloads to .txt as urls so it can be rerun later muahahahhaah
if len(failed_downloads) > 0:
    failed_downloads_txt = f'failed_downloads_{args.ver}.txt'
    print(f"At least one download failed, saving urls to {failed_downloads_txt}")
    with open(failed_downloads_txt, 'w') as f:
        for fd in failed_downloads:
            f.write(fd + '\n')
sys.exit(0)
