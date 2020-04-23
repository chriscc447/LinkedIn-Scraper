from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pprint import PrettyPrinter
from time import sleep
import pandas as pd
import numpy as np
from collections import deque
from datetime import datetime
from scraper_utils import *
from preprocess_utils import *

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pp = PrettyPrinter(indent = 4)
class LI_Scraper:
    def __init__(self, ref_path = "path.txt"):
            
        self.ref_path = ref_path
        self.col_dict = {col:[] for col in ["source_id", "dest_id", "dest_name", \
            "dest_title", "dest_company", "dest_location", "dest_school", "dest_pic", "dest_childs", "tree_degree"]}
    
        self.df = pd.DataFrame(self.col_dict)
            
        self.processed = set() 
        self.browser = None
    
    def _setup_browser(self):     
        with open(self.ref_path, "r") as f:
            path, username, password = (x.strip("\n") for x in f)

        browser = webdriver.Chrome(path)
        browser.get("https://www.linkedin.com/login/")

        #wait for webpage to load
        
        sleep(3)
        user = browser.find_elements_by_name("session_key")[0]
        user.send_keys(username)

        pwd = browser.find_elements_by_name("session_password")[0]
        pwd.send_keys(password)

        login = browser.find_elements_by_xpath("//button[@type = 'submit']")[0]
        login.click()
        self.browser = browser
    
    def _get_header_info(self):
        header_section = self.browser.find_element_by_xpath("//section[@class = 'pv-top-card artdeco-card ember-view']")
        name = header_section.find_element_by_xpath(".//li[@class = 'inline t-24 t-black t-normal break-words']").text
        
        try:
            pic = header_section.find_element_by_xpath(".//img[@class = 'pv-top-card__photo presence-entity__image EntityPhoto-circle-9 lazy-image loaded ember-view']").get_attribute("src")
        except NoSuchElementException:
            pic = None
        
        return (name, pic)
    
    def _get_background_info(self):
        bg = self.browser.find_element_by_id("oc-background-section").text
        data = []
        try:
            title = parse(bg, "\nTitle")
        except LookupError:
            try:
                title = parse(bg, "Experience")
            except LookupError:
                title = None
        data.append(title)
        
        for q in ["\nCompany Name", "\nLocation", "\nEducation"]:
            try:
                data.append(parse(bg, q))
            except LookupError:
                data.append(None)
        return data  
    
    def _get_related_profiles(self, source_id, n, get_links):
        data = [None, None]
        try:
            check = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH, "//h2[@class = 't-16 t-black t-normal']")))    
            assert check.text.strip().lower() == "people also viewed"

        except (NoSuchElementException, TimeoutException, AssertionError):
            pass

        else:
            related_list = list(enumerate(self.browser.find_elements_by_xpath(".//li[@class = 'pv-browsemap-section__member-container mt4 ember-view']")))
            all_links = [r[1].find_element_by_xpath(".//a[@data-control-name = 'browsemap_profile']").get_attribute("href") for r in related_list]
            all_ids =[extract_id(l) for l in all_links]

            links = []
            if get_links:
                print("Getting links", end = "...")
                cnt = 0
                while related_list and cnt<n:
                    r = related_list.pop(0)
                    rp = r[1].find_element_by_xpath(".//a[@data-control-name = 'browsemap_profile']")

                    #cant scrape profiles that have premium for some reason
                    if rp.find_elements_by_class_name("premium-icon"):
                        continue
                    else:
                        i = r[0]
                        if all_ids[i] not in self.processed:
                            links.append(all_links[i])
                            cnt += 1                        
                data[1] = {"source":source_id, "dest":links}

            id_str =  ",".join(all_ids)
            data[0] = id_str
            
        print("Done")
        return data
        
    
    def _scrape_profile(self, url, n, source_id, degree, get_links):
        profile_dict = self.col_dict.copy()
        
        profile_dict["source_id"] = source_id
        dest_id = extract_id(url)

        profile_dict["dest_id"] = dest_id
        profile_dict["tree_degree"] = degree   
        
        
        print(f"\t\tRetrieving data from [ {url} ]", end = "...")
        self.browser.get(url)
        
        profile_dict["dest_name"], profile_dict["dest_pic"] = self._get_header_info()
        profile_dict["dest_title"], profile_dict["dest_company"], profile_dict["dest_location"], profile_dict["dest_school"] = self._get_background_info()

        data = self._get_related_profiles(url, n, get_links)
        profile_dict["dest_childs"] = data[0]
        
        self.df = self.df.append(profile_dict, ignore_index = True)

        self.processed.add(dest_id)
        return data[1]
    
    def _find_inters(self):
        l = []
        for i in range(len(self.df)):
            str_childs = self.df.loc[i, "dest_childs"]
            if str_childs:
                s = set(str_childs.split(","))
                inter = ",".join(self.processed.intersection(s))
                if not inter: #no intersection
                    l.append(None)
                else:
                    l.append(inter)
            else:
                l.append(None)
        return l 
    
    def run(self, start_url, degrees = 3, connects = 3, save = True, csv_path = "profiles.csv", process = True):
        #set up browser object
        start_time = datetime.now()
        connects = min(connects, 10) #only 10 related profiles displayed
        if not self.browser:
            print("Setting up browser", end = "...")
            self._setup_browser()
            
            if not self.browser:
                return
            
            print("Done")
            print()
        print("Running profile scraper:")
        #bfs on connects
        q = deque()
        
        #track depth, 
        print("\tInitial profile")
        q.append(self._scrape_profile(start_url, connects, None, 0, True))
        depth = 1
        q.append(None)
        
        get_links = True
        
        while len(q) > 0:
            urls = q.popleft()
            if urls is None:
                depth += 1
                if depth >= degrees:
                    get_links = False
                q.append(None)
                urls = q.popleft()
            if urls is None:
                end_time = datetime.now()
                print(f"Profile scraping finished in {str(end_time - start_time)}")
                break
            
            else:
                parent_link = urls["source"]
                parent = extract_id(parent_link)
                
                dest_links = urls["dest"]
                print(f"\n\tDegree of separation: {depth}", end = f"\t\tLinked from: {parent}\n")


                if not dest_links:
                    print(f"\t\t{parent} has no related profiles")
                else:
                    for link in urls["dest"]:
                        if extract_id(link) not in self.processed:
                            related = self._scrape_profile(link, connects, parent, depth, get_links)
                            if related is not None:
                                q.append(related)
        
        self.df["dest_connected"] = self._find_inters()
        
        if process:
            print("\nPreprocessing DataFrame", end = "...")
            self.df = preprocess(self.df)
            print("Done")
        if save:
            self.save(csv_path)
            
    def save(self, csv_path = "profiles.csv"):
        print(f"Saving DataFrame to {csv_path}")
        self.df.to_csv(csv_path, index = False)