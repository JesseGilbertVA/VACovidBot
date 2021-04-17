# Import necessary modules.
import requests
import tweepy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import date
import time
import config

# Get today's date, then make it a string.
today_raw = date.today()
today = today_raw.strftime('%A, %B %d, %Y')

# Authenticate with Twitter.
auth = tweepy.OAuthHandler(config.apiKey, config.apiSecretKey)
auth.set_access_token(config.accessToken, config.accessTokenSecret)
api = tweepy.API(auth)

# Declare URL and configure Firefox driver to be used in headless mode.
url = 'https://www.worldometers.info/coronavirus/country/us/'
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get(url)

# Actual scraping code. Getting case and death data then formatting it to be used in later functions.
sortByState = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div/div[5]/div[1]/div/table/thead/tr/th[2]')
driver.execute_script("arguments[0].scrollIntoView();", sortByState)
sortByState.click()
soup = BeautifulSoup(driver.page_source, 'html.parser')
tr = soup.findAll('tr')
virginia = tr[48]
data = virginia.findAll('td')
rawCases = data[2]
rawDeaths = data[4]
getCases = rawCases.get_text()
getDeaths = rawDeaths.get_text()
stripCases = str(getCases).strip('\n').replace(',', '')
stripDeaths = str(getDeaths).strip('\n').replace(',', '')
intCases = int(stripCases)
intDeaths = int(stripDeaths)

# Compare cases obtained from scraping to last run's cases.
def casesDifferenceFunc():
    readCasesFile = open('cases.txt', 'r')
    readCases = readCasesFile.read()
    casesDifference = intCases - int(readCases)
    return casesDifference

# Same as above but for deaths.
def deathsDifferenceFunc():
    readDeathsFile = open('deaths.txt', 'r')
    readDeaths = readDeathsFile.read()
    deathsDifference = intDeaths - int(readDeaths)
    return deathsDifference

# Overwriting previous saved data if a change was detected.
def writeFiles():
    writeCasesFile = open('cases.txt', 'w')
    writeCasesFile.write(stripCases)
    writeDeathsFile = open('deaths.txt', 'w')
    writeDeathsFile.write(stripDeaths)
    return print('Files written successfully')

# Run the above functions then format the data to be sent in tweet.
newCasesRaw = casesDifferenceFunc()
newCases = " (+" + "{:,}".format(newCasesRaw) + ")"
newDeathsRaw = deathsDifferenceFunc()
newDeaths = " (+" + "{:,}".format(newDeathsRaw) + ")"
cases = "{:,}".format(intCases)
deaths = "{:,}".format(intDeaths)


try:
    api.verify_credentials() # Verify authentication succeeded.
    print('Authentication OK')
    if newCases == ' (+0)' and newDeaths == ' (+0)': # If no new cases, terminate script.
        print('Cases and deaths are the same, closing script.')
        driver.quit()
    else: # If there are new cases, send tweet.
        api.update_status('Virginia COVID-19 cases and deaths as of ' + today + ':\n\nCases: ' + cases + newCases + '\nDeaths: ' + deaths + newDeaths + '\n\n#COVID19 #Coronavirus #Pandemic #Virginia')
        print('Virginia COVID-19 cases and deaths as of ' + today + ':\n\nCases: ' + cases + newCases + '\nDeaths: ' + deaths + newDeaths + '\n\n#COVID19 #Coronavirus #Pandemic #Virginia')
        print('Tweet sent successfully.')
        writeFiles()
        time.sleep(10)
        driver.quit()

except:
    print('Error during authentication')