from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import requests
import time
import os

EC.url_changes
class Pa:
    paths = {
        "emailInput": '''//*[@id="sign_content"]/div[2]/div[1]/div/div[3]/div/div[1]/div/div/div[1]/div/input''',
        "passInput": '''//*[@id="sign_content"]/div[2]/div[1]/div/div[3]/div/div[2]/div/div/div[1]/div/input''',
        "signInButton": '''//*[@id="sign_content"]/div[2]/div[1]/div/div[3]/div/div[4]/button/span/span''',
        "9:16Button": '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[1]/div[2]/div[3]/div[2]/div[2]/div[1]/div[2]/span''',
        "2Image": '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[1]/div[2]/div[3]/div[3]/div/div[2]/span''',
        "PromptArea": '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div/div[1]/textarea''',
        "GenerateButton": '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[1]/div[2]/button''',
        "Image1Path": [
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div/div/div/div[4]/div/div[1]/img''',
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div/div[4]/div/div[1]/img''',
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div/div[3]/div/div[1]/img'''
        ],
        "Image2Path": [
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div/div/div/div[4]/div/div[2]/img''',
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div/div[4]/div/div[2]/img''',
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div/div[3]/div/div[2]/img'''
        ],
        "GeneratingTextPath": [
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[4]/div[2]/div[1]/div/div[2]/div[3]''',
            '''//*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[2]'''
            ''' //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg''',
        ]

    }
    def driversetup(self):
        try:
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1366,768)
            self.driver = driver
        except:
            raise ValueError("Driver setup failed")
            
    def signin(self,email,password,maxTime):
        try:
            self.driver.get("https://www.piclumen.com/app/account/login")
            def clickElement(key,inputText):
                element = WebDriverWait(self.driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, self.paths[key]))
                    )
                element.click()
                element.send_keys(inputText)
            keys = ["emailInput","passInput","signInButton"]

            n = 0
            clickElement(keys[n],email)
            print("email entered scessfully")
            n +=1
            clickElement(keys[n],password)
            print("Password entered seccesfully")
            n += 1
            element = WebDriverWait(self.driver, 4).until(
            EC.element_to_be_clickable((By.XPATH, self.paths[keys[n]]))
            )
            element.click()
            print("signin button clicked Scessfully")

            startTime = time.time()
            WebDriverWait(self.driver,maxTime).until(EC.url_changes("https://www.piclumen.com/app/account/login"))
        except:
            raise ValueError(f'''!!!!!!!!!!!v
                  fix {keys[n]} path
                  !!!!!!!!!''')
    def nevigateSetup(self):
        try:
            print("Nevigating and intracting")
            self.driver.get("https://www.piclumen.com/app/create")
            try:
                WebDriverWait(self.driver, 10).until(EC.title_contains("Generate"))
            except:
                raise ValueError("Can't open create website")
            

            def clickAndCheck(button):
                element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, self.paths[button])))
                element.click()
                # if element.value_of_css_property("background-color") != "rgb(40 40 40)":
                #     raise ValueError(f'''!!!!!!!!!!!!!!!!!!!!!!
                #                     Faild to click {button} setting
                #                     !!!!!!!!!!!!!!!!!!!!!!!!!''')
            
            clickAndCheck("2Image")
            time.sleep(1)
            clickAndCheck("9:16Button")
        except:
            raise ValueError("Problem in creating process")
    
    # def modelSelecter(self,)
    def generateImage(self,prompt):
        try:
            element = WebDriverWait(self.driver, 4).until(
                                EC.element_to_be_clickable((By.XPATH, self.paths["PromptArea"]))
                                )
            element.click
            element.clear
            element.send_keys(prompt)
            element = WebDriverWait(self.driver, 4).until(
                                EC.element_to_be_clickable((By.XPATH, self.paths["GenerateButton"]))
                                )
            element.click()
        except:
            raise ValueError('''!!!!!!!!!!!!!!!!!!
                            problem in image creation''')
    def generationInProgress(self,maxTime,checkPerTime,maxDownloadTime,downloadCheckPerTime):
        startTime = time.time() 

        while (time.time() - startTime) < maxTime:
            found = False
            for path in self.paths["GeneratingTextPath"]:
                try:
                    element = self.driver.find_element(By.XPATH, path)
                    print("Generation ")
                    break
                except:
                    continue
            else:
                time.sleep(checkPerTime)
            if found:
                break
        else:
            raise ValueError("can't cornform if generation started")
        
        startTime = time.time()
        while (time.time() - startTime) < maxDownloadTime:
            try:
                element = self.driver.find_element(By.XPATH, self.paths["GeneratingTextPath"])
                if element:
                    time.sleep(downloadCheckPerTime)
                    continue
                else:
                    break
            except:
                raise ValueError("got an error while check generation status")
            
        

        
    def downloadImage(self,name,imgno):
        try:
            for i in self.paths[f"Image{imgno}Path"]:
                try:
                    element = self.driver.find_element(i)
                    break
                except:
                    continue
            
            imageLink = element.get_attribute("src")
            print(f"Found image link {imageLink}")
            imageObj = requests.get(imageLink)
            with open(name,"w") as imageFile:
                imageFile.write(imageObj.content)
            print(f"Downloaded image at {name}")
        except:
            raise ValueError("faild to download image")

def automate_pa(dataList):
    baseEmail, password, reelFolder, imagePerId, promptStartNo, maxCheckGeneratingTime, checkPerTime, maxDownloadTime, downloadCheckPerTime, numberOfImg, tries, startId = dataList

    with open(os.path.join(reelFolder,"prompts.txt"),"r",encoding="utf-8") as promptFile:
        prompts = [i.strip() for i in promptFile if i.strip()]

    
    t = 0
    while t < tries and promptStartNo < len(prompts):
        try:
            imageNo = 0
            reel = Pa()
            reel.driversetup()
            reel.signin(f"{baseEmail}+{startId}@gmail.com",password,maxCheckGeneratingTime)
            reel.nevigateSetup()
            while promptStartNo < len(prompts) and imageNo < imagePerId:
                reel.generateImage(prompts[promptStartNo])
                time.sleep(2)
                with open("source.html","w",encoding="utf-8") as htmlf:
                    htmlf.write(reel.driver.page_source)
                reel.generationInProgress(maxCheckGeneratingTime,checkPerTime,maxDownloadTime,downloadCheckPerTime)
                for i in range(1,numberOfImg+1):
                    reel.downloadImage(prompts[promptStartNo].split()[0],i)
                promptStartNo += 1
            imageNo += 1
            startId += 1
        except ValueError:
            raise
        except:
            print('''!!!!!!!!!!Got a problem trying again!!!!!!!!!!!!!''')
            t += 1
            startId += 1
            continue
        


def process_reels(baseFolder): #makes a list of paths of reel folders
    reelPaths = []
    for reelFolder in os.listdir(baseFolder): #get path of each folder one by one
        if reelFolder.isdigit():  #checks if its a folder of reel or not 
            reelPaths.append(os.path.join(baseFolder, reelFolder))

    return reelPaths    



if __name__ == "__main__":
    
    baseFolder = input("Enter Base Folder:- ")
    baseEmail = "imagemaker2928"
    password = "Hello_word"
    startId = int(input("Enter the starting email ID: "))
    imagePerId = 5
    promptStartNo = 0
    maxCheckGeneratingTime = 20
    checkPerTime = 1
    maxDownloadTime = 20
    downloadCheckPerTime = 1
    numberOfImg = 2
    tries = 3


    reelPaths = process_reels(baseFolder)
    dataList = (baseEmail, password, reelPaths[0],imagePerId,promptStartNo,maxCheckGeneratingTime,checkPerTime,maxDownloadTime,downloadCheckPerTime, numberOfImg, tries, startId)

    automate_pa(dataList)
    


# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[4]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]

# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div[1]/div[1]/div/div/div/svg
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg[1]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg[1]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg[1]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/i/svg




# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[4]/div[2]/div[1]/div/div[2]/div[3]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[4]/div[2]/div[1]/div/div[2]/div[3]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[2]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[2]
# //*[@id="__nuxt"]/div/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[2]