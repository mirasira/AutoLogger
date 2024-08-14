from playwright.sync_api import sync_playwright
import datetime
import time
import os
import json

def main():
    print("AutoLogger started")
    Username, Password, GCList, LogText, DoScreenshots, Date = readConfig()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Log in
        CheckForGDPR(page)
        page.goto("https://www.geocaching.com/account/signin?returnUrl=")
        page.wait_for_load_state()
        CheckForGDPR(page)
        page.wait_for_load_state()
        text_field = page.locator('#UsernameOrEmail')
        text_field.fill(Username)
        text_field = page.locator('#Password')
        text_field.fill(Password)
        button = page.locator('#SignIn')
        button.click()
        if DoScreenshots:
            page.screenshot(path='screenshotLogin.png')

        # Search list
        page.goto("https://www.geocaching.com/plan/lists/" + GCList)
        page.wait_for_load_state()
        CheckForGDPR(page)
        page.wait_for_load_state()
        if DoScreenshots:
            page.screenshot(path='screenshotList.png')
        
        
        Element = '//*[@id="__next"]/div/div[1]/div/section/div[1]/div[2]/span[2]/div/div[2]'
        text_field = page.locator(Element)
        text = text_field.inner_text()
        text = text.split("/")[-1]
        print("Number of caches: " + text)
        

        GCCodes = []

        for i in range(int(text)):
            for j in range(1, 4):
                # find text field
                ElementArray = []
                # Element = "#__next > div > div.page-container.flex.flex-col.flex-grow.items-center > div > section > div.flex.relative.max-w-full.overflow-x-auto.overflow-y-visible.print\:scrollbar.print\:scrollbar-w-0 > table > tbody > tr:nth-child("+ str(i+1) + ") > td.list-geocache-details > div > div.geocache-details > div.geocache-meta > span:nth-child(" + str(j+1) + ")"
                # ElementArray.append(Element)

                Element = "#__next > div > div.page-container.flex.flex-col.flex-grow.items-center > div.list-details-6h9smn > section > div.flex.relative.max-w-full.overflow-x-auto.overflow-y-visible.print\:scrollbar.print\:scrollbar-w-0 > table > tbody > tr:nth-child(" + str(i+1) + ") > td.list-geocache-details > div > div.geocache-details > div.geocache-meta > span:nth-child(" + str(j+1) + ")"
                ElementArray.append(Element)
                # Element = '//*[@id="__next"]/div/div[1]/div/section/div[' + str(j+1) + ']/table/tbody/tr[' + str(i+1) + ']/td[1]/div/div[2]/div[2]/span[2]'
                for Element in ElementArray:
                    if page.query_selector(Element) != None:
                        text_field = page.locator(Element)
                        text = text_field.inner_text()
                        GCCodes.append(text)

        print("Caches to log: " + str(GCCodes))
        print("Number of caches: " + str(len(GCCodes)))

        for GCCode in GCCodes:
            page.goto("https://www.geocaching.com/live/geocache/"+ GCCode +"/log")
            page.wait_for_load_state()
            CheckForGDPR(page)
            page.wait_for_load_state()
            button = page.locator('//*[@id="__next"]/div/div[1]/main/div/div[2]/div/form/div[1]/label/div/div/div[2]')
            button.click()
            page.wait_for_load_state()
            CacheName = page.locator('#__next > div > div.page-container.flex.flex-col.flex-grow.items-center > main > div > div.content-container > div > section > h2 > a')
            CacheName = CacheName.inner_text()
            if DoScreenshots:
                page.screenshot(path='screenshotLog.png')
            button = page.get_by_text('Found it')

            
            # button = page.locator("button:text('Didn't find it')")
            if button == None:
                continue
            try:
                button = page.wait_for_selector("text='Nalezeno'", timeout=1000)
                button.click()
            except:
                print("Already logged " + GCCode + " " + CacheName)
                continue
            page.wait_for_load_state()
            if DoScreenshots:
                page.screenshot(path='screenshotFoundIt.png')
            text_field = page.locator('//*[@id="gc-md-editor_md"]')
            text_field.fill(LogText)

            if DoScreenshots:
                page.screenshot(path='screenshotLogText.png')

            # set the correct date
            # Date is in format "YYYY-MM-DD"
            # transfrom date to numbers 
            Year, Month, Day = Date.split("-")

            button = page.locator('//*[@id="log-date"]')
            button.click()
            page.wait_for_load_state()
            page.fill("body > div.flatpickr-calendar.animate.arrowTop.arrowLeft.open > div.flatpickr-months > div > div > div > input", Year)
            # text_field = page.locator('/html/body/div[3]/div[1]/div/div/div/input')
            # text_field.fill(Year)
            page.wait_for_load_state()
            DropDown = page.locator('body > div.flatpickr-calendar.animate.arrowTop.arrowLeft.open > div.flatpickr-months > div > div > select')
            months = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]
            # month = datetime.date(1900, int(Month), 1).strftime('%B')
            month = months[int(Month)-1]
            DropDown.select_option(value=month)
            page.wait_for_load_state()

            # get first day of the month
            firstField = 0
            while True:
                firstField += 1
                Element = 'body > div.flatpickr-calendar.animate.arrowTop.arrowLeft.open > div.flatpickr-innerContainer > div > div.flatpickr-days > div > span:nth-child(' + str(firstField) + ')'
                # get text on the button
                text_field = page.locator(Element)
                text = text_field.inner_text()
                if text == "1":
                    break
            Element = 'body > div.flatpickr-calendar.animate.arrowTop.arrowLeft.open > div.flatpickr-innerContainer > div > div.flatpickr-days > div > span:nth-child(' + str(firstField + int(Day) - 1) + ')'
            button = page.locator(Element)
            button.click()
            page.wait_for_load_state()
            if DoScreenshots:
                page.screenshot(path='screenshotDate.png')

            # submit log
            button = page.locator('#__next > div > div.page-container.flex.flex-col.flex-grow.items-center > main > div > div.content-container > div > form > div.css-1febl34.eu7msjx0 > div.post-button-container > button')
            button.click()
            page.wait_for_load_state()
            if DoScreenshots:
                page.screenshot(path='screenshotSubmit.png')

            print("Logged " + GCCode + " " + CacheName)
            page.wait_for_load_state()
            time.sleep(1)


        

def CheckForGDPR(page):
    Element = '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
    if(page.query_selector(Element)!=None):
        print("GDPR")
        button = page.locator(Element)
        button.click()

def readConfig():
    with open('InputData.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        Username = data['Username']
        Password = data['Password']
        GCList = data['GCList']
        LogText = data['LogText']
        DoScreenshots = data['DoScreenshots']
        Date = data['Date']
    return Username, Password, GCList, LogText, DoScreenshots, Date







if __name__ == "__main__":
    main()






