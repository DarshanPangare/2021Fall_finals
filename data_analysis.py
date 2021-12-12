import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
pd.options.mode.chained_assignment = None  # default='warn'

pd.options.plotting.backend = "plotly"


def get_hyp1_data(): -> pd.DataFrame:
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
    df = pd.read_csv("Dataset/wfp_market_food_prices.csv",
                     encoding="ISO-8859-1")
    food_data = df.rename(columns={"adm0_id": "country_id", "adm0_name": "country_name", "adm1_id": "locality_id",
                                   "adm1_name": "locality_name", "mkt_id": "market_id", "mkt_name": "market_name",
                                   "cm_id": "commodity_id", "cm_name": "commodity_name", "cur_id": "currency_id",
                                   "cur_name": "currency_name", "pt_id": "market_type_id", "pt_name": "market_type",
                                   "um_id": "measurement_id", "um_name": "unit", "mp_month": "month", "mp_year": "year",
                                   "mp_price": "price", "mp_commoditysource": "source_information"})
    country_data = pd.read_excel(
        f"Dataset/Country_status_price.xlsx")
    comb_data = food_data.merge(country_data, left_on='country_name', right_on='country_name')
    comb_data['usd_price'] = comb_data['price'] * comb_data['price_factor']
    combined_data = comb_data[
        ['country_name', 'commodity_name', 'month', 'year', 'price', 'country_status', 'price_factor', 'usd_price']]
    return combined_data


def select_data(combined_data: pd.DataFrame, country1: str, country2: str, commodity: str) -> pd.DataFrame:
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
    selective_data = combined_data.loc[
        ((combined_data.country_name == country1) | (combined_data.country_name == country2)) & (
                combined_data.commodity_name == commodity)]
    return selective_data


def plot_data(combined_data: pd.DataFrame, country1: str, country2: str, commodity: str)-> None:
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
    return None


def calc_corr(combined_data: pd.DataFrame, country1: str, country2: str, commodity: str) -> tuple:
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


# Hypothesis 2

def get_storm_data() -> pd.DataFrame:
    """
    This function creates a empty dataframe and merges all the storm datasets from the year 2019 to 2011 by reading it
    as a csv file. As there were many storms in the dataset, we are only considering the significant storms by
    taking the values greater than 96. Later on we group by the number of storms occurred in a month.
    :return: This functions returns a dataframe.
    >>> get_storm_data()
        YEAR MONTH_NAME  count_storm
    0   2011       July           20
    1   2011   December            7
    2   2011      April            6
    3   2011      March            4
    4   2011   November            4
    ..   ...        ...          ...
    68  2019   November            3
    69  2019   December            2
    70  2019   February            2
    71  2019       July            1
    72  2019    October            1
    <BLANKLINE>
    [73 rows x 3 columns]
    """
    storm_df = pd.DataFrame()
    for i in range(19, 10, -1):
        storm_df = storm_df.append(pd.read_csv(
            f'Dataset/StormEvents_details-ftp_v1.0_d20{i}.csv'))
    storm_df = storm_df[['BEGIN_YEARMONTH', 'BEGIN_DAY', 'BEGIN_TIME', 'END_YEARMONTH', 'END_DAY', 'END_TIME',
                         'EPISODE_ID', 'EVENT_ID', 'STATE', 'YEAR', 'MONTH_NAME', 'EVENT_TYPE', 'DAMAGE_PROPERTY',
                         'DAMAGE_CROPS', 'MAGNITUDE']]

    storm_df = storm_df[storm_df['MAGNITUDE'] >= 96]
    storm_df_short = storm_df[['YEAR', 'MONTH_NAME']]
    storm_df_grouped = storm_df_short.groupby('YEAR')['MONTH_NAME'].value_counts().reset_index(name='count_storm')
    return storm_df_grouped


def get_date(row: pd.DataFrame) -> str:
    """
    This function converts the Year and Month column to a proper date-time format so that it could become easier to
    visualize and plot them correctly.
    :param row: Returns the Year and Month column in date time format
    :return: Returns a string of the date time format
    >>> get_date([2011, "July"])
    datetime.datetime(2011, 7, 1, 0, 0)
    """
    try:
        date = str(row[0]) + " " + str(row[1])
        return datetime.strptime(date, '%Y %B')
    except:
        print(row[0], row[1])
        return np.nan


def find_for_crop(crop_name: list, data: pd.DataFrame, storm_df_grouped: pd.DataFrame) -> str:
    """
    This function joins the two main dataset. The result_df is dataframe where we calculate the difference between the
    current value of the commodities and the price of that commodity after a month as the storm will have it's effect
    after a particular period of time. Later we plot the graphs for various commodities against year after normalizing
    the values.
    :param crop_name: A list of all the agricultural commodities which are going to be compared
    :param data: This is the crop dataset that is parsed
    :param storm_df_grouped: This is the storm dataset that is parsed
    :return: It will return the plots and the pearsonr value

    # >>> find_for_crop("Apples", pd.read_csv('FAOSTAT_data_all_crops_data.csv'), pd.DataFrame([2011, "July", 20]))
    """
    crop_df = data[data['Item'] == crop_name][['Year', 'Months', 'Value']]
    # crop_data1 = crop_data[['Year', 'Months']]
    # Merge the datasets
    result_df = crop_df.merge(storm_df_grouped, how='inner',
                              left_on=['Year', 'Months'], right_on=['YEAR', 'MONTH_NAME'])
    # Converting into the date time function
    if len(result_df) > 0:
        result_df['Date'] = result_df.apply(get_date, axis=1)
    else:
        print('No data for this crop')
        return None
    result_df = result_df.drop(['Year', 'Months'], axis=1)
    result_df = result_df.sort_values('Date')
    # Shifting the values price by month to find the proper difference between the
    result_df['Price_shift'] = result_df['Value'].shift(1)
    result_df['Value - Price_shift'] = result_df['Value'] - result_df['Price_shift']
    result_df['count_storm'] = result_df['count_storm'].astype('int32')
    result_df['Value'] = result_df['Value'].astype('int32')
    # Normalizing the values
    result_df['count_storm'] = (result_df['count_storm'] - result_df['count_storm'].min()) / (
            result_df['count_storm'].max() - result_df['count_storm'].min())
    result_df['Value - Price_shift'] = (result_df['Value - Price_shift'] - result_df['Value - Price_shift'].min()) / (
            result_df['Value - Price_shift'].max() - result_df['Value - Price_shift'].min())
    # Plotting
    f1 = result_df.plot(x="Date", y=["Value - Price_shift", "count_storm"], kind="line", title=crop_name)
    # f1.show()
    f2 = px.scatter(result_df['Value - Price_shift'], result_df['count_storm'], trendline="ols", title=crop_name)
    # f2.show()
    result_df = result_df.drop([0, 1], axis=0)
    # Calulated the pearsonr value to find the correlation and P value
    return f1, f2, pearsonr(result_df['Value - Price_shift'], result_df['count_storm'])
