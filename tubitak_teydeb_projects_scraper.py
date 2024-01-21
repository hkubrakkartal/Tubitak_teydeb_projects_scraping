# Libraries
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from time import sleep
import pandas as pd

# Get Data Function
def getData(row, index, id):
   
    data = []
    info_elements = row.find_elements(By.XPATH, f'//*[@id="projeBilgileri_{int(id)-1}"]/table/tbody/tr')
    for info_element in info_elements:
        value = info_element.find_element(By.XPATH, "./td[2]").text
        data.append(value)

    return data


op = Options()   
op.add_argument("--proxy-server='direct://'")
op.add_argument("--proxy-bypass-list=*")
op.add_argument("--start-maximized")
op.add_argument('--ignore-certificate-errors')
op.add_argument('--ignore-ssl-errors')
op.add_experimental_option("excludeSwitches", ["enable-logging"])

path =(r"your_chromedriver.exe_path") # chromedriver.exe path
driver = webdriver.Chrome(executable_path=path, options=op)

# Get URL
url = 'https://eteydeb.tubitak.gov.tr/teydebtamamlanmisprojeler.htm'
driver.get(url)

# Wait for the page to load before continuing
sleep(5)

# keywords, start_year and end_year
keywords = input("Anahtar Kelimeleri Giriniz (Birden fazla ise virgül ile ayırarak giriniz.): ")
anahtarKelimeler = driver.find_element(By.XPATH,"//input[@name='anahtarKelimeler']")
anahtarKelimeler.clear()
anahtarKelimeler.send_keys(keywords)

start_year = input("Yıl Aralığı İlk Sütun: ")
yil1 = driver.find_element(By.XPATH,"//input[@name='yil1']")
yil1.clear()
yil1.send_keys(start_year)

end_year = input("Yıl Aralığı İkinci Sütun: ")
yil2 = driver.find_element(By.XPATH,"//input[@name='yil2']")
yil2.clear()
yil2.send_keys(end_year)

driver.find_element(By.NAME, 'submit').click()

sleep(1)

# Start Scraping
wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.ID, "row")))

allData = []
while True:
    rows = driver.find_elements(By.XPATH, "//*[@id='row']/tbody/tr")
    
    for i, r in enumerate(rows):
        project_id = r.find_elements(By.XPATH,".//td")[0].text
        r.find_elements(By.XPATH,".//td")[3].find_element(By.XPATH,".//a").click() # Open project info
        sleep(0.5)
        values = getData(r,i, project_id) # get data info
        allData.append(values)
        r.find_element(By.XPATH, f'//*[@id="projeBilgileri_{int(project_id)-1}"]/div/a').click() # Close project info
        
    try:
        # Find an element containing the text "sonraki sayfa>"
        next_page_element = driver.find_element(By.XPATH, "//a[contains(text(), 'sonraki sayfa>')]")

        # If the "sonraki sayfa>" element is not found, the end of the page has been reached
    except NoSuchElementException:
        print('Sayfa Sonuna Geldi')
        break

    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'sonraki sayfa>')]"))
    )
    next_button.click()

    WebDriverWait(driver, 12).until(
        EC.staleness_of(next_button)
    )
    
# Close WebDriver
driver.quit()


columnList = ['Proje Adı','Kuruluş Adı','Kuruluş Yılı','Anahtar Kelimeler','Proje Başlama-Bitiş Tarihi','Bilimsel Teknolojik Faaliyet Alanı',
             'Ar-Ge Çalışmalarının Yürütüleceği Sektör','Proje Çıktılarının Kullanılacağı Sektör','Projenin Özeti','Projenin Amacı',
              'Proje Çıktılarının Teknik Özellikleri']
df = pd.DataFrame(allData, columns=columnList)

# Write to Excel file 
filename = 'teydeb_projects_data.xlsx'  
df.to_excel(filename, index=False)

print(f'{filename} dosyası olusturuldu.')