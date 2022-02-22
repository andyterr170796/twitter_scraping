from sys import exit
import pandas as pd
import re
import calendar
import time
import os
import platform
import sys
import numpy as np
import time
from urllib.request import urlretrieve #pip install resumable-urlretrieve
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

# Variables a cambiar
class twitter_scraping:
    def __init__(self,correo,contra,driver_path='',chromedriver=''):
        self.correo = correo
        self.contra = contra
        if driver_path!='':
            self.driver_path = driver_path
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(self.driver_path, chrome_options=options)
            self.chromedriver = chromedriver
        else:
            self.driver_path = driver_path
            self.driver = chromedriver

    def logging_in(self):
        print("logging into:", self.correo)          
        self.driver.get("https://twitter.com/")
        time.sleep(1)
        self.driver.find_element(By.XPATH,"//a[@data-testid='loginButton']").click()
        time.sleep(3)
        self.driver.find_element(By.XPATH,"//input[@autocomplete='username']").send_keys(self.correo)
        a = self.driver.find_elements(By.XPATH,"//div[@role='button']")
        a[2].click()
        time.sleep(3)
        self.driver.find_element(By.XPATH,"//input[@autocomplete='current-password']").send_keys(self.contra)
        self.driver.find_element(By.XPATH,"//div[@data-testid='LoginForm_Login_Button']").click()
        time.sleep(5)

    def buscando_extrae(self,busqueda,bajas=1):
        # Entrando a explorar
        self.driver.find_element(By.XPATH,"//a[@data-testid='AppTabBar_Explore_Link']").click()
        time.sleep(2)
        
        twitter = []
        tweets = []
        users = []
        perf = []
        fecha = []
        links=[]
        likes=[]
        retweets=[]
        replies=[]
        quote=[]
        tema=[]
        
        # Obtención de Tweets
        self.driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']").send_keys(busqueda[0])
        self.driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']").send_keys(Keys.ENTER)
        time.sleep(2)    
        a = self.driver.find_elements(By.XPATH,"//div[@role='tablist']/div[@role='presentation']")
        a[1].click()
        time.sleep(3)
        
        for i in range(0,len(busqueda)):
            if i>0:
                self.driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']").send_keys(Keys.CONTROL, 'a')
                self.driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']").send_keys(Keys.BACKSPACE)
                self.driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']").send_keys(busqueda[i])
                self.driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']").send_keys(Keys.ENTER)
                time.sleep(3)
            lll=1500  
            for j in range(0,bajas): # cantidad veces a scroll
                # Bajamos un poco la página
                #nombres.append(name)
                time.sleep(3)    
                if j>0:
                    bajar = 'window.scrollBy(0,' + str(lll) + ')'
                    self.driver.execute_script(bajar)
                    time.sleep(1)
                a = self.driver.find_elements(By.XPATH,"//div[contains(@aria-label,'Cronología')]/div/div") # cantidad de tweets
                b = self.driver.find_elements(By.XPATH,"//div[contains(@aria-label,'Cronología')]/div/div//a")
                if len(a)==0:
                    a = self.driver.find_elements(By.XPATH,"//div[contains(@aria-label,'Timeline')]/div/div") # cantidad de tweets
                    b = self.driver.find_elements(By.XPATH,"//div[contains(@aria-label,'Timeline')]/div/div//a")
                for z in range(0,len(b)):
                    u=re.findall("/status/\d+",b[z].get_attribute("href"))
                    if len(u)>0:
                        if "photo" not in b[z].get_attribute("href") and "media_tag" not in b[z].get_attribute("href") and "people" not in b[z].get_attribute("href"):
                            links.append(b[z].get_attribute("href"))  
                            tema.append(busqueda[i])
    
        # remueve duplicados
        links=list(dict.fromkeys(links))
        self.driver.get(links[1])
        time.sleep(4)

        # Scraping de cada Tweet
        for zz in range(0,len(links)):
            print(links[zz])
            self.driver.get(links[zz])
            time.sleep(2)
            try:
                a=self.driver.find_element(By.XPATH,"//article[@data-testid='tweet']")
                # demás
                #print(a.text)
                z = re.split("\n",a.text)
                twitter.append(z)
                users.append(twitter[0][0])
                perf.append(twitter[0][1])
                #fecha.append(twitter[0][-3:])
                tweets.append(" ".join(twitter[0][2:]))
                twitter = []
                #print(j)
                
            except:
                pass
                
            try:
                n = re.findall("\d+  Like",tweets[zz])
                l = re.findall("\d+",n[0])
                likes.append(l[0])
            except:
                likes.append("")

            try:
                n = re.findall("\d+  Retweet",tweets[zz])
                l = re.findall("\d+",n[0])
                retweets.append(l[0])
            except:
                retweets.append("")
            
            try:
                n = re.findall("\d+  Repl",tweets[zz])
                l = re.findall("\d+",n[0])
                replies.append(l[0])
            except:
                replies.append("")
            
            try:
                n = re.findall("\d+  Quote Tweet",tweets[zz])
                l = re.findall("\d+",n[0])
                quote.append(l[0])
            except:
                quote.append("")
            
            
            try:
                n = re.findall("([A-Z][a-z]{2}\s\d+,\s\d+)",tweets[zz])
                fecha.append(n[0])
            except:
                fecha.append(tweets[zz][2:8]+", 2022")

        # Formación de base de datos en Excel
        columns = ["Palabra busqueda","Usuario","Perfil","Tweet","Links","Fecha","Likes","RT","Replies","Quotes"]    
        data = list(zip(tema,users,perf,tweets,links,fecha,likes,retweets,replies,quote))
        data = pd.DataFrame(data,columns=columns)

        def fechando(text):
            ao = text[-4:]
            mes = text[0:3]
            map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Set": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
            mes = map[mes]
            dia = text[4:6]
            if "," in dia:
                dia = re.sub(",","",dia)
                dia = "0"+dia
            fecha = ao + "-" + mes + "-" + dia
            print(fecha)
            return fecha
        
        for i in range(0,len(data)):
            try:
                a = fechando(data["Fecha"][i])
                data["Fecha"][i] = a
            except:
                pass
        
        try:
            data1=pd.read_excel("Twitter_scraping.xlsx",index=False)
            data = [data1,data]
            data = pd.concat(data)
        except:
            pass
        
        data=data.drop_duplicates()
        data.to_excel("Twitter_scraping.xlsx",index=False)
