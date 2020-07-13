#!/usr/bin/env python
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:


# with open("university_towns.txt") as f:
#     f_1 = [line.strip("\n") for line in f]
#     for number, line in enumerate(f_1, 1):
#         print (number, line)
        

uni_towns = pd.read_fwf("university_towns.txt", header=None)

def filter_data():
    uni_towns_filtered =[]
    regions = []
    for line in uni_towns.iloc[:, 0]:
        if "[edit]" in line:
            state = line.split("[")[0].strip()
        else:
            uni_towns_filtered.append((state, line.split("(", 1)[0].strip()))
            
#     print (len(uni_towns_filtered))
            
    
    
    return uni_towns_filtered

#uni_towns_filtered = filter_data()

#l = [len(i) for i in uni_towns_filtered.values()]
#print ("Length", sum(l)+len(uni_towns_filtered))
# print (len(uni_towns_filtered))
# print (uni_towns_filtered["Georgia"])



# print (uni_towns.head(100))


def get_list_of_university_towns():
    
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    uni_towns_filtered = filter_data()
    pf = pd.DataFrame(uni_towns_filtered, columns=["State", "RegionName"])
#     print (pf.head())

    return pf

get_list_of_university_towns()



# In[4]:


gdp = pd.read_excel("gdplev.xls", skiprows=5)
gdp.drop(gdp.columns[[3,7]], axis=1, inplace=True)
gdp = gdp.iloc[2:,:]
gdp = gdp.rename(columns={gdp.columns[0]:"Y", gdp.columns[3]: "Q"})
gdp.reset_index(drop=True, inplace=True)

def get_recession_data():
    gdp_rec = gdp.iloc[:,[3, 5]]
    gdp_rec.set_index(gdp["Q"], drop=True, inplace=True)
    gdp_rec = gdp_rec.iloc[gdp_rec.index.get_loc('2000q1'):,:]
    gdp_rec = gdp_rec.rename(columns={gdp_rec.columns[-1]:"GDP chained"})
    return gdp_rec
    

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdp_rec = get_recession_data()

    
    for i in range(1, len(gdp_rec)-1):
        if (gdp_rec.iloc[i-1, 1] > gdp_rec.iloc[i, 1]) & (gdp_rec.iloc[i, 1] > gdp_rec.iloc[i+1, 1]):
#             return gdp_rec.iloc[i, 0]
            return gdp_rec.index[i]
        
    return None

get_recession_start()


# In[5]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdp_rec = get_recession_data()
    rec_start = gdp_rec.index.get_loc(get_recession_start())

    for i in range(rec_start+2, len(gdp_rec)-1):
        if (gdp_rec.iloc[i-1, 1] < gdp_rec.iloc[i, 1]) & (gdp_rec.iloc[i-1, 1] > gdp_rec.iloc[i-2, 1]):
           return gdp_rec.index[i]
    return None

get_recession_end()


# In[6]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp_rec = get_recession_data()
    rec_start = gdp_rec.index.get_loc(get_recession_start())
    rec_end = gdp_rec.index.get_loc(get_recession_end())
    rec_bottom = gdp_rec.index[gdp_rec["GDP chained"] == gdp_rec[rec_start:rec_end+1]["GDP chained"].min()][0]

    return rec_bottom

get_recession_bottom()


# In[7]:



# def convert_housing_data_to_quarters():
#     '''Converts the housing data to quarters and returns it as mean 
#     values in a dataframe. This dataframe should be a dataframe with
#     columns for 2000q1 through 2016q3, and should have a multi-index
#     in the shape of ["State","RegionName"].
    
#     Note: Quarters are defined in the assignment description, they are
#     not arbitrary three month periods.
    
#     The resulting dataframe should have 67 columns, and 10,730 rows.
    
#     '''
#     data = pd.read_csv("City_Zhvi_AllHomes.csv")
#     data = (data.replace(to_replace='NaN', value=np.nan)
#                   .replace({'State': states}))
#     col_years =  list(data.columns[data.columns.get_loc('2000-01'):])
#     cols = ["State", "RegionName"] + col_years
#     data =  data.loc[:, cols] 
    
#     dict_dataframe = {}
    
#     for date in col_years:
#         [year, month] = date.split("-")
#         if month <= "03":
#             if year+"q1" not in dict_dataframe:
#                 dict_dataframe[year+"q1"] = []
#             dict_dataframe[year+"q1"].append(date)
#         elif month <= "06":
#             if year+"q2" not in dict_dataframe:
#                 dict_dataframe[year+"q2"] = []
#             dict_dataframe[year+"q2"].append(date)
#         elif month <= "09":
#             if year+"q3" not in dict_dataframe:
#                 dict_dataframe[year+"q3"] = []
#             dict_dataframe[year+"q3"].append(date)
#         else:
#             if year+"q4" not in dict_dataframe:
#                 dict_dataframe[year+"q4"] = []
#             dict_dataframe[year+"q4"].append(date) 
            
#     new_dataframe = data[["State", "RegionName"]]
    
#     for date1, date2 in dict_dataframe.items():
#         new_dataframe[date1] = data[date2].mean(axis=1)
        
#     new_df = new_dataframe.sort_values(["State", "RegionName"]).set_index(["State", "RegionName"])
#     #new_df = new_dataframe.set_index(["State", "RegionName"])

#     #print (new_df.shape)
#     return new_df


# convert_housing_data_to_quarters()

def get_quarter(year, month):
    if month <= 3:
        quarter = 1
    elif month <= 6:
        quarter = 2
    elif month <= 9:
        quarter = 3
    elif month <= 12:
        quarter = 4
    return (str(year) + 'q' + str(quarter))

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    df = (df.drop(['RegionID', 'Metro', 'CountyName', 'SizeRank'], axis=1)
             .replace({'State': states})
             .set_index(['State', 'RegionName'])
             .replace(to_replace='NaN', value=np.NaN)
             .convert_objects(convert_numeric=True)
             .sort())
    index = list(df.columns.values).index('2000-01')
    df = df.drop(df.columns[:index], axis=1)
    l = len(df.columns)
    i = 0
    while i < l:
        col_name = df.iloc[:, i].name
        year = int(col_name.split('-')[0])
        month = int(col_name.split('-')[1])
        quarter = get_quarter(year, month)
        if i + 3 < l:
            split = df.iloc[:, i:i + 3]
        else:
            split = df.iloc[:, i:l]
        df[quarter] = split.mean(axis=1)
        i += 3
    df = df.drop(df.columns[:l], axis=1)
    return df


convert_housing_data_to_quarters()


# In[8]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).
    
    Hypothesis: University towns have their mean housing prices less effected by recessions. 
    Run a t-test to compare the ratio of the mean price of houses in university towns the quarter
    before the recession starts compared to the recession bottom. 
    (price_ratio=quarter_before_recession/recession_bottom)
    
    '''

    
    housing_price_recession = convert_housing_data_to_quarters()
    rec_start = get_recession_start()
    rec_bot = get_recession_bottom()

    rec_start_min_1 = housing_price_recession.columns.get_loc(rec_start)-1
    rec_bot = housing_price_recession.columns.get_loc(rec_bot)
    
    housing_price_recession['ratio'] = housing_price_recession.iloc[:,rec_start_min_1]/housing_price_recession.iloc[:,rec_bot]
    df_ratio = pd.DataFrame(housing_price_recession['ratio'])
    
    uni_towns_list = get_list_of_university_towns()
    uni_towns_list = uni_towns_list.set_index(["State", "RegionName"])
    
    
    uni_towns = pd.merge(df_ratio, uni_towns_list, how="inner", left_index=True, right_index=True)
    non_uni_towns = pd.merge(df_ratio, uni_towns_list, how="outer", left_index=True, right_index=True, indicator=True)
    non_uni_towns = non_uni_towns['ratio'][non_uni_towns['_merge']=="left_only"]
    non_uni_towns = non_uni_towns.to_frame()
    print (len(uni_towns))  #should be 269
    print (len(non_uni_towns)) # should be 10461
    uni_towns = uni_towns.dropna()
    non_uni_towns = non_uni_towns.dropna()
    
    test = ttest_ind(uni_towns['ratio'], non_uni_towns['ratio'])
    
    mean_uni = uni_towns['ratio'].mean()
    print (mean_uni) #should be 1.0545...
    mean_non_uni = non_uni_towns['ratio'].mean() #should be 1.0753
    print (mean_non_uni)
    p = test[1]
    difference = True if p<0.01 else False
    better = "university town" if mean_uni < mean_non_uni else "non-university town"
    
    answer = difference, p, better
    
    return answer

run_ttest()



# In[ ]:




