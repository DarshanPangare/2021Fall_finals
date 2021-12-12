import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

df = pd.read_csv("/Users/dp/Desktop/SEM 1/IS597PR/Final_Project/Datasets/Food_dataset/wfp_market_food_prices.csv", encoding = 'unicode_escape')
# df

#Rename all the columns
food_data = df.rename(columns={"adm0_id": "country_id", "adm0_name": "country_name", "adm1_id": "locality_id", "adm1_name": "locality_name", "mkt_id": "market_id", "mkt_name": "market_name", "cm_id": "commodity_id", "cm_name": "commodity_name", "cur_id" : "currency_id", "cur_name" : "currency_name", "pt_id" : "market_type_id", "pt_name" : "market_type", "um_id": "measurement_id", "um_name" : "unit", "mp_month": "month", "mp_year": "year", "mp_price": "price", "mp_commoditysource" : "source_information"})
# food_data

country_data = pd.read_excel("/Users/dp/Desktop/SEM 1/IS597PR/Final_Project/Datasets/Food_dataset/Country_status_price.xlsx")
# country_data

comb_data = food_data.merge(country_data, left_on = 'country_name', right_on = 'country_name')
comb_data['usd_price'] = comb_data['price'] * comb_data['price_factor']
# comb_data

# Exclude unecessary columns
combined_data = comb_data[['country_name', 'commodity_name', 'month', 'year', 'price', 'country_status', 'price_factor', 'usd_price']]
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
    >>> select_data("India", "Pakistan", "Wheat") # doctest : +NORMALIZE_WHITESPACE +ELLIPSIS
            country_id country_name  ...  price_factor usd_price
    157245         115        India  ...        0.0130   0.16250
    157246         115        India  ...        0.0130   0.17550
    157247         115        India  ...        0.0130   0.19500
    157248         115        India  ...        0.0130   0.16068
    157249         115        India  ...        0.0130   0.15600
    ...            ...          ...  ...           ...       ...
    446346         188     Pakistan  ...        0.0057   0.19950
    446347         188     Pakistan  ...        0.0057   0.19950
    446348         188     Pakistan  ...        0.0057   0.19950
    446349         188     Pakistan  ...        0.0057   0.19950
    446350         188     Pakistan  ...        0.0057   0.19950
    <BLANKLINE>
    [5929 rows x 21 columns]
   	"""
    selective_data = combined_data.loc[((combined_data.country_name == country1) | (combined_data.country_name == country2)) & (food_data.commodity_name == commodity)]
    return selective_data

def calc_diff(group: pd.DataFrame):
    """
    Calculates the difference between consecutive food prices

    :param group: dataframe of the selected countries and commodity
    :return: original dataframe with an additional column consisting of price difference values
    >>> d = select_data("India", "Pakistan", "Wheat")
    >>> calc_diff(d) # doctest : +NORMALIZE_WHITESPACE +ELLIPSIS
            country_id country_name  locality_id  ... price_factor  usd_price usd_chng
    157245         115        India         1510  ...       0.0130    0.16250      NaN
    157246         115        India         1510  ...       0.0130    0.17550  0.01300
    157247         115        India         1510  ...       0.0130    0.19500  0.01950
    157248         115        India         1510  ...       0.0130    0.16068 -0.03432
    157249         115        India         1510  ...       0.0130    0.15600 -0.00468
    ...            ...          ...          ...  ...          ...        ...      ...
    446346         188     Pakistan         2272  ...       0.0057    0.19950  0.00000
    446347         188     Pakistan         2272  ...       0.0057    0.19950  0.00000
    446348         188     Pakistan         2272  ...       0.0057    0.19950  0.00000
    446349         188     Pakistan         2272  ...       0.0057    0.19950  0.00000
    446350         188     Pakistan         2272  ...       0.0057    0.19950  0.00000
    <BLANKLINE>
    [5929 rows x 22 columns]

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

    #     Find a common minimum and maximum year for the selected countries and commodity, to be set as x limits

    q1, q2 = subset_data[subset_data['year'] == subset_data.groupby(subset_data['country_name'])['year'].min().max()][
                 'year'].unique(), \
             subset_data[subset_data['year'] == subset_data.groupby(subset_data['country_name'])['year'].max().min()][
                 'year'].unique()

    #     Create a list of unique years to be used as x labels

    unique_yrs = []
    for year in subset_data['year'].unique():
        if year in range(q1[0], q2[0] + 1):
            unique_yrs.append(year)

    new_data = subset_data.groupby(['country_name', 'year'])['usd_price'].mean().reset_index()
    t = new_data.groupby('country_name').apply(lambda x: calc_diff(x))
    ax1 = sns.lineplot(data=t, x="year", y="usd_price", ci=None, hue="country_name", sort=True, marker='o')
    ax1.set_xticks([i for i in unique_yrs])
    ax1.set_xlim(q1[0], q2[0])
    ax1.set_xlabel("Year", fontsize=20)
    ax1.set_ylabel("Commodity Price in USD", fontsize=20)
    ax1.set_title('Developing v/s Underdeveloped Country', fontsize=20)
    sns.set(rc={'figure.figsize': (12, 10)})
    plt.legend(loc=2, bbox_to_anchor=(1, 1), prop={"size": 20})
    plt.show()

def calc_corr(country1, country2, commodity):
    """
    Calculates the correlation coefficient and p-value for the two countries and the selected commodity
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: Pearson correlation coefficient and p-value
    >>> calc_corr("India", "Pakistan", "Wheat")
    (0.22274829066815113, 0.2640932178164745)
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

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
