import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

def get_hyp1_data():
    """
    :return: a dataframe with all the required data/columns
    >>> get_hyp1_data() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
            country_name          commodity_name  ...  price_factor  usd_price
    0       Afghanistan                   Bread  ...        0.0100    0.50000
    1       Afghanistan                   Bread  ...        0.0100    0.50000
    2       Afghanistan                   Bread  ...        0.0100    0.50000
    3       Afghanistan                   Bread  ...        0.0100    0.50000
    4       Afghanistan                   Bread  ...        0.0100    0.50000
    ...             ...                     ...  ...           ...        ...
    743909  South Sudan                  Sesame  ...        0.0023    0.92000
    743910  South Sudan           Fuel (diesel)  ...        0.0023    0.02875
    743911  South Sudan           Fuel (diesel)  ...        0.0023    0.21850
    743912  South Sudan  Fuel (petrol-gasoline)  ...        0.0023    0.21850
    743913  South Sudan  Fuel (petrol-gasoline)  ...        0.0023    0.21551
    <BLANKLINE>
    [743914 rows x 8 columns]
    """
    df = pd.read_csv("/Users/dp/Desktop/SEM 1/IS597PR/Final_Project/Datasets/Food_dataset/wfp_market_food_prices.csv", encoding = "ISO-8859-1")
    food_data = df.rename(columns={"adm0_id": "country_id", "adm0_name": "country_name", "adm1_id": "locality_id", "adm1_name": "locality_name", "mkt_id": "market_id", "mkt_name": "market_name", "cm_id": "commodity_id", "cm_name": "commodity_name", "cur_id" : "currency_id", "cur_name" : "currency_name", "pt_id" : "market_type_id", "pt_name" : "market_type", "um_id": "measurement_id", "um_name" : "unit", "mp_month": "month", "mp_year": "year", "mp_price": "price", "mp_commoditysource" : "source_information"})
    country_data = pd.read_excel("/Users/dp/Desktop/SEM 1/IS597PR/Final_Project/Datasets/Food_dataset/Country_status_price.xlsx")
    comb_data = food_data.merge(country_data, left_on = 'country_name', right_on = 'country_name')
    comb_data['usd_price'] = comb_data['price'] * comb_data['price_factor']
    combined_data = comb_data[['country_name', 'commodity_name', 'month', 'year', 'price', 'country_status', 'price_factor', 'usd_price']]
    return combined_data


def select_data(combined_data, country1, country2, commodity):

    """
    Creates a dataframe based on the selected countries and commodity
    :param combined_data: Dataframe containing all the columns
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: a dataframe with the selected countries and
    >>> temp_df = get_hyp1_data()
    >>> select_data(temp_df, "India", "Pakistan", "Wheat") # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
           country_name commodity_name  ...  price_factor  usd_price
    157245        India          Wheat  ...        0.0130    0.16250
    157246        India          Wheat  ...        0.0130    0.17550
    157247        India          Wheat  ...        0.0130    0.19500
    157248        India          Wheat  ...        0.0130    0.16068
    157249        India          Wheat  ...        0.0130    0.15600
    ...             ...            ...  ...           ...        ...
    446346     Pakistan          Wheat  ...        0.0057    0.19950
    446347     Pakistan          Wheat  ...        0.0057    0.19950
    446348     Pakistan          Wheat  ...        0.0057    0.19950
    446349     Pakistan          Wheat  ...        0.0057    0.19950
    446350     Pakistan          Wheat  ...        0.0057    0.19950
    <BLANKLINE>
    [5929 rows x 8 columns]
   	"""
    selective_data = combined_data.loc[((combined_data.country_name == country1) | (combined_data.country_name == country2)) & (combined_data.commodity_name == commodity)]
    return selective_data



def plot_data(combined_data, country1, country2, commodity):
    """
    Plots a line graph with 'Year' on x-axis and the 'Price' of commodity on the y-axis
    :param combined_data: Dataframe containing all the columns
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: Plots a line graph
    """
    selective_data = select_data(combined_data, country1, country2, commodity)
    new = selective_data.groupby(['country_name', 'year'])['usd_price'].mean().reset_index()
    new['pct'] = new['usd_price'].pct_change().fillna(0)
    new.sort_values(by='year', inplace=True)

    #     Find a common minimum and maximum year for the selected countries and commodity, to be set as x limits

    q1, q2 = new[new['year'] == new.groupby(new['country_name'])['year'].min().max()][
                 'year'].unique(), \
             new[new['year'] == new.groupby(new['country_name'])['year'].max().min()][
                 'year'].unique()

    #     Create a list of unique years to be used as x labels

    unique_yrs = []
    for year in new['year'].unique():
        if year in range(q1[0], q2[0] + 1):
            unique_yrs.append(year)

    ax1 = sns.lineplot(data=new, x="year", y="pct", ci=None, hue="country_name", sort=True, marker='o')
    ax1.set_xticks([i for i in unique_yrs])
    ax1.set_xlim(q1[0], q2[0])
    ax1.set_xlabel("Year", fontsize=20)
    ax1.set_ylabel("% Change in Price", fontsize=20)
    ax1.set_title('Developing v/s Underdeveloped Country', fontsize=20)
    sns.set(rc={'figure.figsize': (12, 10)})
    plt.legend(loc=2, bbox_to_anchor=(1, 1), prop={"size": 20})
    plt.show()

def calc_corr(combined_data, country1, country2, commodity):
    """
    Calculates the correlation coefficient and p-value for the two countries and the selected commodity
    :param combined_data: Dataframe containing all the columns
    :param country1: Name of developing country
    :param country2: Name of an underdeveloped country
    :param commodity: Name of a commodity
    :return: Pearson correlation coefficient and p-value
    >>> temp_df = get_hyp1_data()
    >>> combined_data = select_data(temp_df, "India", "Pakistan", "Wheat")
    >>> calc_corr(combined_data, "India", "Pakistan", "Wheat")
    (0.22274829066815113, 0.2640932178164745)
    """
    _data = select_data(combined_data, country1, country2, commodity)
    q1, q2 = _data[_data['year']==_data.groupby(_data['country_name'])['year'].min().max()], _data[_data['year']==_data.groupby(_data['country_name'])['year'].max().min()]
    result = pd.concat(([q1, q2]))
    a = len(result.loc[result['country_name']== country1, 'usd_price'].tolist())
    b = len(result.loc[result['country_name']== country2, 'usd_price'].tolist())
    if a < b:
        corr_value = pearsonr(result.loc[result['country_name']== country1, 'usd_price'].tolist(), result.loc[result['country_name']== country2, 'usd_price'].tolist()[:a])
    elif a > b:
        corr_value = pearsonr(result.loc[result['country_name']== country1, 'usd_price'].tolist()[:b], result.loc[result['country_name']== country2, 'usd_price'].tolist())
    else:
        corr_value = pearsonr(result.loc[result['country_name']== country1, 'usd_price'].tolist(), result.loc[result['country_name']== country2, 'usd_price'].tolist())
    return corr_value