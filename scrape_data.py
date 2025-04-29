from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import requests as re

#initializing chrome driver with service,options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
options = Options()
options.add_argument('--disable-notifications')
# driver = webdriver.Chrome()
#open IMDB website
#url = "https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31"
#url = "https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&genres=action"


#Scraping Genres list
#enres = ["Action","Animation","Crime","Music","Sport"]
genres = ["War"]

#Store all data in single dataframe
consolidated_df = pd.DataFrame()

for genre in genres:
    url = f"https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&genres={genre}"
    driver.get(url)
    time.sleep(5)
    #options.page_load_strategy = 'normal'
    #driver.maximize_window()

    #try-catch block for more options
    def click_more_option():
        try:
            #more_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH,'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[2]/div/span/button/span/span')))
            more_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH,'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[2]/div/span/button')))

            ActionChains(driver).move_to_element(more_option).perform()
            more_option.click()
            
            return True
        except Exception as e:
            print("Unable to click More option:", e)
            return False

    #to check for load more option is available
    while click_more_option():
        print("More option is clicked")

    #Consider there is no more data to load
    print("As there is no data available for", genre,"'More option' is absent.")
    
    #Initialize list
    movie_Names = []
    ratings = []
    voting_Counts = []
    durations = []


#Expand Genre

    whole_content = driver.find_elements(By.XPATH,'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li')
    # actions = ActionChains(driver)
    # #actions.move_to_element(whole_content).perform()
    # whole_content.click()

    for movie_item in whole_content:
        try:
            #Extract movie_Name, rating, voting_Count and duration
            movie_Name = movie_item.find_element(By.XPATH,'./div/div/div/div[1]/div[2]/div[1]/a/h3').text
            rating = movie_item.find_element(By.XPATH,'./div/div/div/div[1]/div[2]/span/div/span/span[1]').text
            voting_Count = movie_item.find_element(By.XPATH,'./div/div/div/div[1]/div[2]/span/div/span/span[2]').text
            duration = movie_item.find_element(By.XPATH,'./div/div/div/div[1]/div[2]/div[2]/span[2]').text
        
            #Adding data into lists
            movie_Names.append(movie_Name)
            ratings.append(rating)
            voting_Counts.append(voting_Count)
            durations.append(duration)
        except Exception as e:
            print("Error in data extraction:")
            continue


    df = pd.DataFrame({
        'Movie_Name': movie_Names,
        'Rating': ratings,
        'Voting_Count': voting_Counts,
        'Duration': durations,
        'Genre': genre
    })
    df['Movie_Name'] = df['Movie_Name'].str.replace(r'^"?\d+\.\s*', '', regex=True) 
    df['Movie_Name'] = df['Movie_Name'].str.replace('"', '', regex=False)  
        
    #df['Title'] = df['Title'].str.replace(r'^\d+\,\s*', '', regex=True)
    df['Voting_Count'] = df['Voting_Count'].str.replace(r'[\(\)]', '', regex=True)

    df.to_csv(f"{genre}_movies.csv", index=False)

    consolidated_df = pd.concat([consolidated_df, df], ignore_index=True)

#Movies_df = pd.DataFrame(movie_data)  # assuming movie_data is your list of dicts
#Movies_df.to_csv("Movies.csv", index=False)

driver.quit()

#Store all data in single file
consolidated_df.to_csv("IMDB_2024_movies.csv", index=False)

#-----------Data Cleaning-------------
consolidated_df['Movie_Name'] = consolidated_df['Movie_Name'].str.replace(r'^"?\d+\.\s*', '', regex=True) 
consolidated_df['Movie_Name'] = consolidated_df['Movie_Name'].str.replace('"', '', regex=False)   


def voting_Count_Conversion(self):
        self = str(self).replace(',', '')  
        if 'K' in self.upper():
            return int(float(self[:-1]) * 1000)
        elif 'L' in self.upper():
            return int(float(self[:-1]) * 100000)
        elif 'M' in self.upper():
            return int(float(self[:-1]) * 1000000)
        else:
            return int(float(self)) 


def duration_into_minutes_conversion(duration):
    duration = str(duration).lower().strip()
    hours = minutes = 0
    hr_match = re.search(r'(\d+)\s*h', duration)
    min_match = re.search(r'(\d+)\s*m', duration)
    if hr_match:
        hours = int(hr_match.group(1))
    if min_match:
        minutes = int(min_match.group(1))
    return hours * 60 + minutes

consolidated_df['Voting_Count'] = consolidated_df['Voting_Count'].apply(voting_Count_Conversion)
consolidated_df['Duration'] = consolidated_df['Duration'].apply(duration_into_minutes_conversion)
    #Store all data in single dataframe
                         
    


  
# ------
#     df['Voting_Count'] = df['Voting_Count'].str.replace(r'[^0-9.]', '', regex=True).astype(float)
#     def voting_Count_Conversion(self):
#         self = self.strip().upper()  # Remove leading/trailing spaces and standardize case
#         if 'K' in self:
#             return int(float(self.replace('K', '').strip()) * 1000)
#         elif 'L' in self:
#             return int(float(self.replace('L', '').strip()) * 100000)
#         elif 'M' in self:
#             return int(float(self.replace('M', '').strip()) * 1000000)
#         else:
#             return int(float(self.strip()))  # Direct conversion
        
    

#     def duration_into_minutes_conversion(duration):
#         duration = str(duration).lower().strip()
#         hours, minutes = 0
#         hrs_match = re.search(r'(\d+)\s*h', duration)    #(r'(\d+)\s*h', duration)
#         mins_match = re.search(r'(\d+)\s*m', duration)      #(r'(\d+)\s*m', duration)
#         if hrs_match:
#             hours = int(hrs_match.group(1))
#         if mins_match:
#             minutes = int(mins_match.group(1))
#         return hours * 60 + minutes

#     df['Voting_Count'] = df['Voting_Count'].apply(voting_Count_Conversion)
#     df['Duration'] = df['Duration'].apply(duration_into_minutes_conversion)

#     # #remove h & m from duration
#     #df['Duration'] = df['Duration'].str.replace(r'[^0-9 ]', '', regex=True)

#     # split duration into hours & minutes and convert to total duration
#     # df[['Hours', 'Minutes']] = df['Duration'].str.split('Hours', expand=True).astype(int)
#     # df['Total_duration'] = df['Hours']* 60 + df['Minutes'].astype(int)
#     # df['Total_duration'] = df['Total_duration'].astype(str)

#     df.to_csv(f"{genre}_2024_movies_IMDB.csv", index=False)
#     consolidated_df = pd.concat([consolidated_df, df], ignore_index=True)

# # # Save combined CSV

# consolidated_df.to_csv("All_genres_2024_movies_IMDB.csv", index=False)
# print("\n All genres are saved in all_genres_2024_movies_IMDB.csv")

# driver.quit()
