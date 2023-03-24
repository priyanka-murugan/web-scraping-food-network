#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
import os
from time import time
from multiprocessing.pool import ThreadPool
from re import match
import time
from string import ascii_lowercase as alc
import pymongo
import datetime


fn_url = "https://www.foodnetwork.com/recipes/recipes-a-z/"
my_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
path_fn_az = "food_network_a-z/"
file_names_az = os.listdir(path_fn_az)

# creating an alphabet list
alphabet_list = []

for j in alc:
    alphabet_list.append(j)


def saveString(html, filename):
    try:
        file = open(filename,"w", encoding='utf-8')
        file.write(str(html))
        file.close()
    except Exception as ex:
        print('Error: ' + str(ex))

def loadString(f):
    try:
        html = open(f, "r", encoding='utf-8').read()
        return(html)
    except Exception as ex:
        print('Error: ' + str(ex))


# To sort the files/folders in alphabetical order
def sort_key(s):
    return int(s.split('_')[-1].split('.')[0])


# Creating alphabetical directories
def create_alphabetical_folders():
    for i in alphabet_list:
        try:
            os.mkdir("food_network_"+i + "/")
            print("Directory " + i + " created")
        except: 
            print("already exists!")


# Define a function to convert the text into minutes
def convert_to_minutes(text):
    # Split the text into days, hours, and minutes
    parts = text.split()
    days = 0
    hours = 0
    minutes = 0
    for i, part in enumerate(parts):
        if part == "day" or part == "days":
            days = int(parts[i-1])
        elif part == "hr" or part == "hrs":
            hours = int(parts[i-1])
        elif part == "min" or part == "mins":
            minutes = int(parts[i-1])
    # Use the timedelta module to calculate the total minutes
    total_minutes = datetime.timedelta(days=days, hours=hours, minutes=minutes).total_seconds() // 60
    return total_minutes


############################### SCRAPING ######################################

# This code will loop through the alphabet list in batches of 4, and wait for 2 minutes between each batch.
# This block of code will take approximately 4 hours to run

def save_alphabetical_webpages():
    az_urls = []
    alphabet_list = []

    for x in alc:
        alphabet_list.append(x) 
    
    for i in range(0, len(alphabet_list[4:]),4 ):
        batch = alphabet_list[i:i+4]
        for j, alp in enumerate(batch):
            az_urls.append(fn_url + alp)
            page_fn = requests.get(az_urls[i+j], headers=my_header, timeout=10)
            soup_fn = bs(page_fn.text, "html.parser")
            item_url = soup_fn.findAll('li', class_='m-PromoList__a-ListItem')
            print(alp)
            for k, item in enumerate(item_url):
                print(k+1)
                print(item.text)
                print('https:' + item.find("a").get("href")[2:])
                url = item.find("a").get("href")
                page_fn_item = requests.get('https:' + url, headers=my_header, timeout=20)
                soup_fn_item = bs(page_fn_item.text, "html.parser")
                saveString(soup_fn_item, "food_network_"+alp+"/" + "recipe_url_"+alp+"_" + str(k) + '.html')
            if j < len(batch) - 1:
                time.sleep(120)

def save_all_chefs_page():
    url_az_ch = "https://www.foodnetwork.com/profiles/talent"
    response = requests.get(url_az_ch)
    soup_az_ch = bs(response.content, 'html.parser')
    saveString(soup_az_ch, "chefs/all_talent_page.html")



############################### A_Z_CHEFS COLLECTION ######################################

# a-z chefs attributes

def a_z_chefs():
    # Record the start time
    start_time = time.time()
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    all_chefs = client["FoodNetworkData"]
    all_chefs_collection = all_chefs["a_z_chefs"]
    all_chefs_collection.create_index("chef_id", unique=True)
    
    file = "chefs/all_talent_page.html"
    with(open(file, 'r', encoding = 'utf-8')) as file_html:
        soup_az_ch = bs(file_html.read(), 'html.parser')
        chefs_links = soup_az_ch.find('div', {'class': 'aToZ section'}).findAll("section", attrs = {'class' : 'o-Capsule o-SiteIndex'})
        for i, link in enumerate(chefs_links):
            alphabet = link.find('span', {'class': "o-Capsule__a-HeadlineText"}).text.strip()
            chefs_list = []
            for item, ch_link in enumerate(link.findAll('li', {'class': 'm-PromoList__a-ListItem'})):
                chefs_dict = {}
                chefs_dict["chef_id"] = "CHE_"+alphabet + "_" + str(item)
                chefs_dict["chef_name"] = ch_link.text.strip()
                chefs_dict["fn_chef_url"] = "https:" + ch_link.find("a").get("href")
                #saveString(soup_fn_item, "chefs/" + alphabet+"_" + "chef_"+ str(item) + '.html')

                page_ch = requests.get(chefs_dict["fn_chef_url"], headers = my_header, timeout = 10)
                soup_ch = bs(page_ch.text, "html.parser")
                item_ch = soup_ch.find("div", attrs = {"class" : "m-MediaBlock o-Capsule__m-MediaBlock"})
                #ch_desc = soup_ch.find("div", attrs = {"class" : "o-Capsule__m-Body"})
                ch_desc = soup_ch.find("div", attrs = {"class" : "m-MediaBlock__a-Description"})

                urls = re.findall(r'href=[\'"]?([^\'" >]+)', str(item_ch))
                try:
                    chefs_dict['chef_description'] = ch_desc.text.strip()
                    # Use regex to remove "Mondays 8|7c" or "8am | 7c"
                    chefs_dict['chef_description'] = re.sub(r'8am\s*\|\s*7c|Mondays\s*8\|\s*7c|Tuesdays\s*9\|\s*8c|Thursdays\s*9\|\s*8c|Thursdays\s*12\|\s*11c|Thursdays\s*10a\|\s*9c', 'N/A', chefs_dict['chef_description'])
                except:
                    chefs_dict['chef_description'] = "N/A"
                
                chefs_dict['facebook']= "N/A"
                chefs_dict['twitter'] = "N/A"
                chefs_dict['pinterest']= "N/A"
                chefs_dict['instagram']= "N/A"
                chefs_dict['youtube'] = "N/A"
                chefs_dict['website'] = "N/A"

                for url in urls:
                    if 'facebook.com' in url:
                        chefs_dict['facebook'] = url
                    elif 'twitter.com' in url:
                        chefs_dict['twitter'] = url
                    elif 'pinterest.com' in url:
                        chefs_dict['pinterest'] = url
                    elif 'instagram.com' in url:
                        chefs_dict['instagram'] = url
                    elif 'youtube.com' in url:
                        chefs_dict['youtube'] = url
                    else:
                        if "foodnetwork" in url:
                            chefs_dict['website'] ="N/A"
                        else:
                            chefs_dict['website'] = url
                
                for key in chefs_dict:
                    print(key)
                    if chefs_dict[key].strip() == "":
                        chefs_dict[key] = "N/A"
                print(chefs_dict)
                all_chefs_collection.insert_one(chefs_dict)           
        # Record the end time
    end_time = time.time()
    
    # Print the time taken to run the function
    print("Time taken:", (end_time - start_time)/60.0, "minutes")


############################### RECIPE_ATTRIBUTES COLLECTION ######################################

# get all the recipe attributes of the recipes
def recipe_attributes():
    # Record the start time
    start_time = time.time()
    
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    all_recipes = client["FoodNetworkData"]
    recipe_attributes = all_recipes["recipe_attributes"]
    recipe_attributes.create_index("recipe_id", unique=True)
    for alp in alphabet_list:
        file_list = [x for x in os.listdir("food_network_"+alp) if '.html' in x]
        file_list.sort(key=sort_key)
        for j, item in enumerate(file_list):
            print("food_network_"+alp+"/" + item)
            pattern = r"url_(.*?)\.html"
            match = re.search(pattern, item)
            result = match.group(1)
            recipe_id = "REC_" + result.upper()
            #print(recipe_id)
            with(open("food_network_"+alp+"/" + item, 'r', encoding = 'utf-8')) as file_html:
                soup_fn_a = bs(file_html.read(), "html.parser")

                attribute_dict = {}
                title_item = soup_fn_a.find('span', attrs = {'class' : 'o-AssetTitle__a-HeadlineText'})
                attribute_dict["recipe_id"] = recipe_id
                attribute_dict["recipe_name"] = title_item.text
                try:
                    recipe_url = soup_fn_a.find('body', attrs = {'class' : 'recipePage'})
                    attribute_dict["recipe_url"] = "https:"+ recipe_url.get("data-shorten-url")
                except:
                    attribute_dict["recipe_url"] = "N/A"

                attribute_dict["fn_chef_url"] = "N/A"
                print(title_item.text)
                try:
                    chef_item = soup_fn_a.find('span', attrs = {'class' : 'o-Attribution__a-Name'}).find("a")
                    attribute_dict["chef_name"] = chef_item.text
                    attribute_dict["fn_chef_url"] = "https:"+ chef_item.get("href")
                    print(chef_item.text)
                    print("https:"+ chef_item.get("href"))
                except:
                    try:
                        chef_item = soup_fn_a.find('span', attrs = {'class' : 'o-Attribution__a-Name'})
                        if(re.findall('^(Recipe)\s(courtesy)\s(of)\s.*',chef_item.text.strip())):
                            attribute_dict["chef_name"] = re.sub('^(Recipe)\s(courtesy)\s(of)\s','', chef_item.text.strip())
                        else:
                            attribute_dict["chef_name"] = chef_item.text

                    except:
                        attribute_dict["chef_name"] = "N/A"

#                 rating_item = soup_fn_a.find('span', attrs = {'class' : 'rating-stars'})
#                 print(rating_item)

                # Yield and Level
                try:
                    yield_item = soup_fn_a.find('ul', attrs = {'class' : 'o-RecipeInfo__m-Yield'}).find("span", attrs = {'class' : 'o-RecipeInfo__a-Description'})  
                    level_item = soup_fn_a.find('ul', attrs = {'class' : 'o-RecipeInfo__m-Level'}).find("span", attrs = {'class' : 'o-RecipeInfo__a-Description'})
                    attribute_dict["yield"] = yield_item.text
                    attribute_dict["level"] = level_item.text
                    # replace level with N/A if it contains hr or min
                    if re.search(r'(hr|min)', attribute_dict["level"]):
                        attribute_dict["level"] = "N/A"
                except:
                    attribute_dict["yield"] = "N/A"
                    attribute_dict["level"] = "N/A"

                # Time
                try:
                    total_time = soup_fn_a.find("span", attrs = {'class' : 'o-RecipeInfo__a-Description m-RecipeInfo__a-Description--Total'})
                    attribute_dict["total"] = convert_to_minutes(total_time.text.strip())
    
                except:
                    attribute_dict["total"] = 0.0

                attribute_dict["prep"] = 0.0
                attribute_dict["cook"] = 0.0
                
                attribute_dict["active"] = 0.0
                attribute_dict["inactive"] = 0.0
                try:
                    preptime = soup_fn_a.find("ul", attrs = {'class' : 'o-RecipeInfo__m-Time'}).findAll("li")   

                    for i, item in enumerate(preptime):
                        key = item.find("span").text.strip().lower()[:-1]
                        value = item.find("span").find_next_sibling("span").text.strip()
                        attribute_dict[key] = convert_to_minutes(value)
                except:
                    pass

                # Ingredient
                try:
                    ingredient = soup_fn_a.findAll("p", attrs = {'class' : 'o-Ingredients__a-Ingredient'})
                    #attribute_dict["ingredients"] = {"N/A"}
                    for ing, item in enumerate(ingredient):
                        key = str(ing+1)
                        value = ingredient[ing].find("span", attrs = {'class' : 'o-Ingredients__a-Ingredient--CheckboxLabel'}).text
                        attribute_dict["ingredients"][key] = value
                except:
                    pass

                # Renaming columns
                key_map = {
                        'total': 'total_time',
                        'prep': 'prep_time',
                        'cook' : 'cook_time',
                        'active' : 'active_time', 
                        'inactive' : 'inactive_time'
                    }

                for old_key, new_key in key_map.items():
                    if old_key in attribute_dict:
                        value = attribute_dict.pop(old_key)
                        attribute_dict[new_key] = value

                print(attribute_dict)
                recipe_attributes.insert_one(attribute_dict)
    # Record the end time
    end_time = time.time()
    
    # Print the time taken to run the function
    print("Time taken:", (end_time - start_time)/60.0, "minutes")
 


############################### RECIPE_SHOWS COLLECTION ######################################

# Get all the show and episode data for the recipes 

def recipe_shows():
    # # Show details if any
    # Record the start time
    start_time = time.time()
    
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    all_recipes_shows = client["FoodNetworkData"]
    recipe_shows = all_recipes_shows["recipe_shows"]
    recipe_shows.create_index("recipe_id", unique=True)
    for alp in alphabet_list:
        file_list = [x for x in os.listdir("food_network_"+alp) if '.html' in x]
        file_list.sort(key=sort_key)
        for j, item in enumerate(file_list):
            print("food_network_"+alp+"/" + item)
            pattern = r"url_(.*?)\.html"
            match = re.search(pattern, item)
            result = match.group(1)
            recipe_id = "REC_" + result.upper()
            #print(recipe_id)
            with(open("food_network_"+alp+"/" + item, 'r', encoding = 'utf-8')) as file_html:
                soup_fn_a = bs(file_html.read(), "html.parser")
                title_item = soup_fn_a.find('span', attrs = {'class' : 'o-AssetTitle__a-HeadlineText'})
                show_dict = {}
                #show_dict['recipe_id'] = recipes_dict["recipe_id"]
    #             show_dict['recipe_name'] = title_item.text
    
                show = soup_fn_a.findAll("div", attrs = {'class' : 'm-MediaBlock__a-Source'})[:2]
                if not show:
                    print("No show data found for recipe:", title_item.text)
                    continue
                for i, item in enumerate(show):
                    show_dict['recipe_id'] = recipe_id
                    show_dict['recipe_name'] = title_item.text
                    key = item.find("span").text.strip().lower()
                    value_name = item.find("span").find_next_sibling("span").text.strip()
                    value_url = "https:" + item.find("span").find_next_sibling("span").find("a").get("href")
                    show_dict[key] = {'name' : value_name, 'url': value_url}
                    key_map = {
                            'show:': 'shows',
                            'episode:': 'episodes',
                            'episodes:' : 'episode_drop'
                        }
                    for old_key, new_key in key_map.items():
                        if old_key in show_dict:
                            value = show_dict.pop(old_key)
                            show_dict[new_key] = value
                            
                try:
                    del show_dict['episode_drop']
                except:
                    pass
                print(show_dict)
                recipe_shows.insert_one(show_dict)
    # Record the end time
    end_time = time.time()
    
    # Print the time taken to run the function
    print("Time taken:", (end_time - start_time)/60.0, "minutes")
            
############################### RECIPE_CATEGORIES COLLECTION ######################################

# get all the categories data for each recipe

# Record the start time
def recipe_categories():
    start_time = time.time()

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    all_recipes_cat = client["FoodNetworkData"]
    categories = all_recipes_cat["recipe_categories"]
    categories.create_index("recipe_id", unique=True)

    catkey = ['recipe_id', 'recipe_name', 'category_id','category_name', 'category_url']
    recipe_dict = {}

    for alp in alphabet_list:
        file_list = [x for x in os.listdir("food_network_"+alp) if '.html' in x]
        file_list.sort(key=sort_key)
        for j, item in enumerate(file_list):
            print("food_network_"+alp+"/" + item)
            pattern = r"url_(.*?)\.html"
            match = re.search(pattern, item)
            result = match.group(1)
            recipe_id = "REC_" + result.upper()
            #print(recipe_id)
            with(open("food_network_"+alp+"/" + item, 'r', encoding = 'utf-8')) as file_html:
                soup_fn_a = bs(file_html.read(), "html.parser")
                title_item = soup_fn_a.find('span', attrs = {'class' : 'o-AssetTitle__a-HeadlineText'})
                recipe_name = title_item.text
                category_dict_list = []
                category = soup_fn_a.findAll("div", attrs = {"class" : 'o-Capsule__m-TagList m-TagList'})
                if not category:
                    print("No category data found for recipe:", recipe_name)
                    continue
                for i, item in enumerate(category[0].findAll("a")):
                    sub_dict = {}
                    for sub_key, sub_value in enumerate(item):
                        sub_dict[f'category_{sub_key}'] = sub_value
                    category_dict = {
                        #catkey[0]: 1,
                        catkey[2]: i+1,
                        catkey[3]: sub_value,
                        catkey[4]: "https:" + item.get("href")
                    }
                    category_dict_list.append(category_dict)
                recipe_dict = {
                    'recipe_id': recipe_id, 
                    'recipe_name': recipe_name,
                    'categories': category_dict_list
                }
                print(recipe_dict)
                categories.insert_one(recipe_dict)
    # Record the end time
    end_time = time.time()
    
    # Print the time taken to run the function
    print("Time taken:", (end_time - start_time)/60.0, "minutes")
            

############################### RECIPE_NUTRITION COLLECTION ######################################

#get all the recipe nutrition for all recipes

def recipe_nutrition():
    ### Nutrition
    start_time = time.time()

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    all_recipes = client["FoodNetworkData"]
    recipe_nutrition = all_recipes["recipe_nutrition"]
    recipe_nutrition.create_index("recipe_id", unique=True)
    for alp in alphabet_list:
        file_list = [x for x in os.listdir("food_network_"+alp) if '.html' in x]
        file_list.sort(key=sort_key)

        for j, item in enumerate(file_list):
            pattern = r"url_(.*?)\.html"
            match = re.search(pattern, item)
            result = match.group(1)
            recipe_id = "REC_" + result.upper()
            #print(recipe_id)
            print("food_network_"+alp+"/" + item)
            with(open("food_network_"+alp+"/" + item, 'r', encoding = 'utf-8')) as file_html:
                soup_fn_a = bs(file_html.read(), "html.parser")
                title_item = soup_fn_a.find('span', attrs = {'class' : 'o-AssetTitle__a-HeadlineText'})
                nutrition = soup_fn_a.findAll("dl", attrs = {"class" : 'm-NutritionTable__a-Content'})
                if not nutrition:
                    print("No nutrition data found for recipe:", title_item.text)
                    continue
                nutrition_dict = {'recipe_id':recipe_id, 
                                  'recipe_name': title_item.text, 
                                  'serving size' : 'N/A', 
                                  'calories' : 0.0,
                                  'total fat' : 0.0,
                                  'saturated fat' : 0.0,
                                  'carbohydrates' : 0.0,
                                  'dietary fiber' : 0.0,
                                  'sugar' : 0.0,
                                  'protein': 0.0, 
                                  'cholesterol' : 0.0, 
                                  'sodium' : 0.0}
                for i in nutrition[0].findAll("dt"):
                    soup_i = bs(str(i), 'html.parser')
                    key = soup_i.text.strip().lower()
                    soup_val = bs(str(i.find_next_sibling('dd')), 'html.parser')
                    value = soup_val.text.strip()
                    nutrition_dict[key] = value
                    pattern = r'\b(\d+(\.\d+)?)\s*(calorie|calories|g|grams?|mg|milligrams?)\b'
                    matches = re.findall(pattern, value)
                    #match = re.match(pattern, value, re.IGNORECASE)

                    if matches:
                        for match in matches:
                            #amount = float(match[0])
                            weight = float(match[0])
                            unit = match[1].lower()
                            # convert to grams
                            if unit == 'g' or unit == 'grams':
                                return weight
                            elif unit == 'mg' or unit == 'milligrams':
                                return weight / 1000
                            else:
                                weight
                        nutrition_dict[key] = weight
                    keys_to_convert = ['calories', 'total fat', 'saturated fat', 'carbohydrates', 'dietary fiber', 'sugar', 'protein', 'cholesterol', 'sodium']
                    for key in keys_to_convert:
                        if key in nutrition_dict:
                            nutrition_dict[key] = float(nutrition_dict[key])

                    key_map = {
                        'total fat': 'total_fat',
                        'saturated fat': 'saturated_fat',
                        'serving size' : 'serving_size',
                        'dietary fiber' : 'dietary_fiber'
                    }

                    for old_key, new_key in key_map.items():
                        if old_key in nutrition_dict:
                            value = nutrition_dict.pop(old_key)
                            nutrition_dict[new_key] = value

                print(nutrition_dict)
                recipe_nutrition.insert_one(nutrition_dict)
            # Record the end time
    end_time = time.time()
    
    # Print the time taken to run the function
    print("Time taken:", (end_time - start_time)/60.0, "minutes")

############################### MAIN Function ######################################

def main():
    start_time = time.time()
    a_z_chefs()
    print("All chefs loaded")
    recipe_attributes()
    print("All recipe attributes loaded")
    recipe_shows()
    print("All shows data loaded")
    recipe_categories()
    print("All categories data loaded")
    recipe_nutrition()
    print("All nutrition data loaded")
    end_time = time.time()
    print("Time taken:", (end_time - start_time)/60.0, "minutes")


def perform_scraping_routine():
    create_alphabetical_folders()
    print("All the folders created!")
    save_alphabetical_webpages()
    print("All the 3000+ recipe pages saved in their alphabetical folders!")
    save_all_chefs_page()
    print("Saved the page with all chefs information!")

choice = input("Do you want to scrape all the pages and save them in folders? Type 'N' because Estimated time is close to 4 hours :( (Y/N)")

if choice == "Y":
    perform_scraping_routine()
else:
    print("Good Choice! All the files are in zip folder that we have created. We will load all the data now :)")
    main()
    print("DONE!")



############################### FIN. ######################################




