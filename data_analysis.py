import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

df = pd.read_csv("/Users/dp/Desktop/SEM 1/IS597PR/Final_Project/Datasets/Food_dataset/wfp_market_food_prices.csv")
# df

#Rename all the columns
food_data = df.rename(columns={"adm0_id": "country_id", "adm0_name": "country_name", "adm1_id": "locality_id", "adm1_name": "locality_name", "mkt_id": "market_id", "mkt_name": "market_name", "cm_id": "commodity_id", "cm_name": "commodity_name", "cur_id" : "currency_id", "cur_name" : "currency_name", "pt_id" : "market_type_id", "pt_name" : "market_type", "um_id": "measurement_id", "um_name" : "unit", "mp_month": "month", "mp_year": "year", "mp_price": "price", "mp_commoditysource" : "source_information"})
# food_data

country_data = pd.read_excel("/Users/dp/Desktop/SEM 1/IS597PR/Final_Project/Datasets/Food_dataset/Country_status_price.xlsx")
# country_data

combined_data = food_data.merge(country_data, left_on = 'country_name', right_on = 'country_name')
combined_data['usd_price'] = combined_data['price'] * combined_data['price_factor']
# combined_data

#Check the data type of all the columns
# combined_data.dtypes

def select_data(country1, country2, commodity):
    """
    Creates a dataframe based on the selected countries and commodity
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: a dataframe with the selected countries and commodity
    >>> select_data("India", "Pakistan", "Wheat") # doctests : +ELLIPSIS

   	country_id	country_name	locality_id	locality_name	market_id	market_name	commodity_id	commodity_name	currency_id	currency_name	...	market_type	measurement_id	unit	month	year	price	source_information	country_status	price_factor	usd_price
157245	115	India	1510	Uttar Pradesh	922	Agra	84	Wheat	68	INR	...	Retail	5	KG	1	2011	12.50	M/o Consumer Affairs, Food and Public Distribu...	Developing	0.0130	0.16250
157246	115	India	1510	Uttar Pradesh	922	Agra	84	Wheat	68	INR	...	Retail	5	KG	2	2011	13.50	M/o Consumer Affairs, Food and Public Distribu...	Developing	0.0130	0.17550
157247	115	India	1510	Uttar Pradesh	922	Agra	84	Wheat	68	INR	...	Retail	5	KG	3	2011	15.00	M/o Consumer Affairs, Food and Public Distribu...	Developing	0.0130	0.19500
157248	115	India	1510	Uttar Pradesh	922	Agra	84	Wheat	68	INR	...	Retail	5	KG	4	2011	12.36	M/o Consumer Affairs, Food and Public Distribu...	Developing	0.0130	0.16068
157249	115	India	1510	Uttar Pradesh	922	Agra	84	Wheat	68	INR	...	Retail	5	KG	5	2011	12.00	M/o Consumer Affairs, Food and Public Distribu...	Developing	0.0130	0.15600
...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...	...
446346	188	Pakistan	2272	Balochistan	295	Quetta	84	Wheat	45	PKR	...	Retail	5	KG	12	2016	35.00	Pakistan Bureau of Statistics	Underdeveloped	0.0057	0.19950
446347	188	Pakistan	2272	Balochistan	295	Quetta	84	Wheat	45	PKR	...	Retail	5	KG	1	2017	35.00	Pakistan Bureau of Statistics	Underdeveloped	0.0057	0.19950
446348	188	Pakistan	2272	Balochistan	295	Quetta	84	Wheat	45	PKR	...	Retail	5	KG	2	2017	35.00	Pakistan Bureau of Statistics	Underdeveloped	0.0057	0.19950
446349	188	Pakistan	2272	Balochistan	295	Quetta	84	Wheat	45	PKR	...	Retail	5	KG	3	2017	35.00	Pakistan Bureau of Statistics	Underdeveloped	0.0057	0.19950
446350	188	Pakistan	2272	Balochistan	295	Quetta	84	Wheat	45	PKR	...	Retail	5	KG	4	2017	35.00	Pakistan Bureau of Statistics	Underdeveloped	0.0057	0.19950
5929 rows × 21 columns
    """
    selective_data = combined_data.loc[((combined_data.country_name == country1) | (combined_data.country_name == country2)) & (food_data.commodity_name == commodity)]
    return selective_data

def calc_diff(group: pd.DataFrame):
    """
    Calculates the difference between consecutive food prices

    :param group: dataframe of the selected countries and commodity
    :return: original dataframe with an additional column consisting of price difference values
    """
    group['usd_chng'] = group.usd_price.diff(1)
    return group


def plot_data(country1, country2, commodity):
    """
    Plots a line graph with 'Year' on x-axis and the 'Price' of commodity on the y-axis
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: Plots a line graph
    """
    subset_data = select_data(country1, country2, commodity)
    subset_data.sort_values(by='year', inplace=True)
    q1, q2 = subset_data[subset_data['year'] == subset_data.groupby(subset_data['country_name'])['year'].min().max()][
                 'year'].unique(), \
             subset_data[subset_data['year'] == subset_data.groupby(subset_data['country_name'])['year'].max().min()][
                 'year'].unique()
    unique_yrs = []
    for year in subset_data['year'].unique():
        if year in range(q1[0], q2[0] + 1):
            unique_yrs.append(year)

    new_data = subset_data.groupby(['country_name', 'year'])['usd_price'].mean().reset_index()
    t = new_data.groupby('country_name').apply(lambda x: calc_diff(x))
    ax1 = sns.lineplot(data=t, x="year", y="usd_price", ci=None, hue="country_name", sort=True, marker='o')
    ax1.set_xticks([i for i in unique_yrs])
    ax1.set_xlim(q1[0], q2[0])
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Price")
#     ax1, ax = plt.subplots(2, 2, sharex=True, figsize=(16,8))
    sns.set(rc = {'figure.figsize':(20,12)})
    plt.show()


def calc_corr(country1, country2, commodity):
    """
    Calculates the correlation coefficient and p-value for the two countries and the selected commodity
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: Pearson correlation coefficient and p-value
    """
    _data = select_data(country1, country2, commodity)
    q1, q2 = _data[_data['year'] == _data.groupby(_data['country_name'])['year'].min().max()], _data[
        _data['year'] == _data.groupby(_data['country_name'])['year'].max().min()]
    result = pd.concat(([q1, q2]))
    a = len(result.loc[result['country_name'] == country1, 'usd_price'].tolist())
    b = len(result.loc[result['country_name'] == country2, 'usd_price'].tolist())
    if a < b:
        corr_value = pearsonr(result.loc[result['country_name'] == country1, 'usd_price'].tolist(),
                              result.loc[result['country_name'] == country2, 'usd_price'].tolist()[:a])
    elif a > b:
        corr_value = pearsonr(result.loc[result['country_name'] == country1, 'usd_price'].tolist()[:b],
                              result.loc[result['country_name'] == country2, 'usd_price'].tolist())
    else:
        corr_value = pearsonr(result.loc[result['country_name'] == country1, 'usd_price'].tolist(),
                              result.loc[result['country_name'] == country2, 'usd_price'].tolist())
    return corr_value


