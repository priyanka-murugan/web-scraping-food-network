# Web Scraping, Database Design and Data Cleaning Process

## Introduction to data source

The data source is Food Network’s website from where I scraped 3000+ recipe pages and
200+ chef pages to capture relevant information. Food Network is a popular website and TV
network that focuses on various cuisines and their cooking procedures. The website features a
wide range of recipes and food-related content that appeals to both amateur and professional
chefs. The site is organized into several categories, including recipes, and food shows.
The recipe section of the website includes thousands of recipes that are searchable by
ingredients, course, cuisine, and dietary restrictions. Each recipe includes a list of ingredients,
step-by-step instructions, nutritional data, and the categories it falls under. The shows section
includes information about the various cooking shows that air on the Food Network TV network
and the recipes that were broadcasted in each episode. Overall, Food Network is a
comprehensive resource for anyone interested in cooking and food.

I have scraped the website by building a custom web scraping routine to create a
comprehensive recipe database. This will act
as a one-stop-shop solution for food lovers who are looking for quick and easy recipes, want to
structure their diet based on nutritional value, and find similar recipes based on categories and
other celebrity chef recipes.

## Description of Scraping routine

I used Python's BeautifulSoup and Requests packages to scrape the website, which
organizes chef and recipe webpages alphabetically. To ensure that I could extract all required
attributes, I first built the scraping routine for a single alphabet page. Once I confirmed that
the routine was working, I scaled it up to all 26 alphabet pages, with 150 recipes per page,
resulting in over 3000 recipe pages. To create a balanced database with the same number of
recipes from each alphabet, I only chose the first page of each alphabet to scrape. Given the
volume of data I was working with, I had to avoid overloading the server with requests and
encountering a timeout error. To address this, I created batches of four alphabet pages, with
600 recipes per batch. I added a two-minute sleep time between batches and a 10-second
delay between each recipe to ensure smooth scraping and avoid any duplication of recipe
pages. In contrast, I was able to scrape the roughly 200 chef websites without the need for
batching or saving pages since it did not pose a risk of causing a timeout error.

## Database Design Description

### 1. MongoDB as Database Choice

I decided to use MongoDB over others, primarily because it offers the flexibility to store
dynamic attributes as embedded documents within a collection. For instance, in the
"recipe_attributes" collection, the "ingredients" variable is dynamic and varies across different
recipes. By saving it as an embedded document, one can easily expand and reveal all the
ingredient items without any further processing. This approach helps to keep the
data organized and makes it easier to work with. I have also adopted the same design
approach for other attributes such as "shows" and "episodes" in the "recipe_shows" collection
and "categories" in the "recipe_categories" collection. By embedding these attributes as
documents, I can store related information together and retrieve it efficiently when needed. For
instance, I have linked the collections using unique identifiers such as “recipe_id” and
“chef_id”. This allowed me to access related information from different collections easily and avoid
data duplication. Finally, MongoDB's high-performance capabilities make it an excellent choice, especially 
since there are more than 3000 recipes. With MongoDB, we can process data quickly and accurately, without compromising
performance or scalability.

### 2. Database Design

I have organized the database into 5 distinct collections with the primary collection being "recipe_attributes," containing
essential information about each recipe, including its name, cooking time, required skill level,
and the chef who created it. This collection serves as a quick reference to
access this crucial information without being overwhelmed by other data. The
"recipe_nutrition" collection includes detailed nutritional information like calories, fats, protein,
and carbohydrates, which is associated with each recipe in the "recipe_attributes" collection.
The "recipe_categories" collection is designed to make it easier to find recipes based
on preferred cuisine or food category. From the embedded documents in the category
variable, one can access the website URL of a specific category, and find other recipes with a
similar profile. The "recipe_shows" collection contains information about the shows and
episodes in which these recipes were featured and broadcasted on Food Network. Finally, the "a_z_chefs" collection has a comprehensive list of
chefs' social media websites.


## Data cleaning, Formatting, and Standardization Process

To ensure data consistency and improve data quality, I took several steps in data processing.
Firstly, I addressed the issue of missing values by replacing them with "N/A" for categorical
variables and "0.0" for numerical variables. I also implemented RegEx and custom functions
to process and standardize certain string variables in our data. For example, in the
"recipe_nutrition" collection, I converted variables containing various weight formats to
"grams" and returned them as float values. I standardized all the time variables in the
"recipe_attributes" collection by creating a function called "convert_to_minutes," which takes
data in various time formats and returns the corresponding time in "minutes" as float values. To
improve data readability, I renamed certain variable names to a more understandable format.
Additionally, I created "recipe_id" and "chef_id" as unique identifiers in our collections and
made them into an index for their respective collections, which improves performance in
searching and querying. 

This is how the final database looks like - 

![alt text](https://github.com/priyanka-murugan/web-scraping-food-network/blob/main/ERD_GP.jpg)

