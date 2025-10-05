import argparse, time, re, sys
from pathlib import Path
from os import listdir
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

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
txt_pattern = re.compile(r'^(?!CON$|PRN$|AUX$|NUL$|COM[1-9]$|LPT[1-9]$)[\w,\s\-.]+\.(?i:txt)$')
if not(bool(txt_pattern.match(args.filename))):
    raise Exception("Invalid file")
# is the version in the right format (i.e. 1.21.9, 1.8, 1.7.3, etc.) also asked chat forr this one too
ver_pattern = re.compile(r'^1\.(?:[1-9]\d?)(?:\.[1-9]\d*)?$')
if not(bool(ver_pattern.match(args.ver))):
    raise Exception("Invalid Minecraft version")
# defaults to fabric unless otherwise specificed
if args.modloader == None:
    args.modloader = 'fabric'

# setting default download directory for the window
modsdir = Path.cwd() / f"mods({args.ver})"
Path(modsdir).mkdir(exist_ok=True) # makes the directory if it doesn't already exist
options = Options()
prefs = {
    "download.default_directory": str(modsdir),
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)


# getting the window open
driver = webdriver.Edge(options=options)
driver.get("https://www.google.com/") # open up a edge window

failed_downloads = [] # keep track of failed downloads

with open(args.filename, 'r') as file:
    for raw_url in file: # go thru all the urls in the file line by line
        raw_url = raw_url.strip() # whtiespace
        if raw_url[0:1] == '#' or raw_url == '':
            continue # skip commented + empty lines
        print(raw_url)
        url = raw_url + "/versions?g=" + args.ver + "&l=" + args.modloader # go to downloads page for specific version and loader
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)

        #print("TRYING TO FIND DOWNLOAD BUTTON")
        try:
            dl = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Download"]')
            #print("DOWNLOAD BUTTON FOUND")
            #print("TRYING TO GET HREF")
            href = dl.get_attribute('href')
            #print(href)
            driver.get(href)
        except NoSuchElementException: # when there's no download bc the ver/loader no updated yet
            #print("NO DOWNLOAD FOUND")
            failed_downloads.append(raw_url)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

print("end")

# check for .crdownload files in the download directory , wait until all downloads are done to close browser
done = False
while not done:
    found_crdownload = False
    for f in listdir(modsdir): # everything in the directory
        file = modsdir / f # the file path
        if file.is_file() and file.suffix == '.crdownload': # if we have a .crdownload file
            found_crdownload = True
            time.sleep(1) # wait one second
            break # break the for loop and check them all again
    # if we get thru the whole file and there are no crdownload files , we are done
    if not found_crdownload:
        done = True
driver.quit()

# save failed downloads to .txt as urls so it can be rerun later muahahahhaah
if len(failed_downloads) > 0:
    failed_downloads_txt = f'failed_downloads_{args.ver}.txt'
    print(f"At least one download failed, saving urls to {failed_downloads_txt}")
    with open(failed_downloads_txt, 'w') as f:
        for fd in failed_downloads:
            f.write(fd + '\n')
else:
    print("All downloads successful")
    
sys.exit(0)