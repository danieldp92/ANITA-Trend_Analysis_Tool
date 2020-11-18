"""
scraper
This module is part of ANITA

This module contains functions for the processing of the main scraping process.
Scraping of individual websites is included in the scrapers folder, every website has it's own specific scraper module
"""

import os
from bs4 import BeautifulSoup
import time
import datetime
from .MarketScraper import MarketIdentifier
import importlib
import pycountry
import requests


def open_folder(folder_path):
    """ Return a list of all .htm and .html files for the given folder
    exports as a list
    :rtype: list
    """
    assert os.path.isdir(folder_path)
    return [os.path.join(root, name)
            for root, dirs, files in os.walk(folder_path)
            for name in files
            if name.endswith((".html", ".htm"))]


def get_soup(file_path):
    """Creates the soup"""
    assert os.path.isfile(file_path)
    return BeautifulSoup(open(file_path), "html.parser")


def determine_market(soup_file):
    """Determine which market the file comes from
    Returns the name of the market and False if there is no market is found"""
    try:
        return MarketIdentifier.identify_market(soup_file).lower()
    except:  # RONALD CHECK!
        return False

def import_market_modules():
    """Initializes a dict with all modules that contain the scrapers for different markets
    returns a dict in this form {market_name : 'module'}"""
    # initialize dict
    parser_dict = {}

    # Find the market modules
    market_list = [file[:-3] for file in list(os.listdir('anita/MarketScraper')) if
                   not (file.startswith('.') or file.startswith('__'))]

    # For all markets import the module into the dict
    for market in market_list:
        # import except these two: the template and the 'MarketIdentifier' that is already imported and is no
        # specific market
        if market not in ['template', 'MarketIdentifier']:
            parser_dict[market] = importlib.import_module('anita.MarketScraper.' + market)
    return parser_dict


def extract_data(all_files_list, market_modules):
    """All data is to be extracted from the given list of files_paths in all_files_list
    It uses classes:
        Web_page  for the main information about the html file
        Product for the data about the products
        Vendor for the data about the vendors
    The function returns a list of json files per page, in the format:
        [{'web_page': web_page_information, 'page_data':page_specific_data}, etc]"""

    # Initialize the list of data
    data = []

    # loop through all the paths in the all_files_list
    for path in all_files_list:
        # Retrieve main information about the individual pages
        soup = get_soup(path)
        market_name = determine_market(soup)
        if market_name is False:
            continue
        page_type = market_modules[market_name].pagetype(soup)
        date = time.mktime(
            datetime.datetime.strptime('/'.join(path.split('/')[-1].split('_')[0:3]), '%Y/%m/%d').timetuple())

        # Create overview object of the main information about the page
        web_page_information = WebPage(path, market_name, page_type, date, soup)

        # Page data for vendor or product pages
        if web_page_information.page_type == 'product':
            page_specific_data = Product(soup, market_modules[web_page_information.market], date)
        elif web_page_information.page_type == 'vendor':
            page_specific_data = Vendor(web_page_information.soup, market_modules[web_page_information.market], date)
        else:
            page_specific_data = None

        # add all info to a list
        data.append({'web_page': web_page_information, 'page_data': page_specific_data})
    return data




class WebPage:
    """Contains general information about the specific file"""

    def __init__(self, file_name, market, page_type, date, soup):
        self.file_name = file_name
        self.market = market
        self.page_type = page_type
        self.soup = soup
        self.date = date


class Product:
    """Parse the soup and extracts the features for the product"""

    def __init__(self, soup, scraper, file_date):
        self.scraper = scraper
        self.name = self.get_name(soup)
        self.vendor = self.get_vendor(soup)
        self.ships_from = self.get_ships_from(soup)
        self.ships_to = self.get_ships_to(soup)
        self.price = self.get_price(soup)
        self.price_eur = Product.get_price_eur(self.price, file_date)
        self.info = self.get_info(soup)
        self.macro_category  = self.get_macro_category(soup)
        self.micro_category  = self.get_micro_category(soup)
        self.feedback = self.get_feedback(soup, file_date)

    def get_name(self, soup):
        """Returns the name of the product"""
        try:
            return self.scraper.p_product_name(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_vendor(self, soup):
        """Returns the name of the vendor"""
        try:
            return self.scraper.p_vendor(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_ships_from(self, soup):
        """Returns the country/area where is shipped from"""
        unclear_names = ['not specified', 'no ships from specified', 'anonymous', 'unspecified', 'undeclared']
        try:
            ships_from = self.scraper.p_ships_from(soup)
            if len(ships_from) == 2:
                ships_from = Product.get_country(ships_from)

            if ships_from.lower() in unclear_names:
                ships_from = 'Unspecified'
            return ships_from
        except:
            return None

    def get_ships_to(self, soup):
        """Returns a list of countries where shipped to"""
        unclear_names = ['not specified', 'no ships from specified', 'anonymous', 'unspecified', 'undeclared']

        try:
            ship_to = self.scraper.p_ships_to(soup)
            # return in a list if only one country is known
            if type(ship_to) == str:
                if len(ship_to) == 2:
                    ship_to = Product.get_country(ship_to)
                if ship_to.lower() in unclear_names:
                    ship_to = 'Unspecified'
                ship_to = [ship_to]

            # Change abbreviations of countries into country names
            for n, country in enumerate(ship_to):
                if len(country) == 2:
                    ship_to[n] = Product.get_country(country)
                if country.lower() in unclear_names:
                    ship_to[n] = 'Unspecified'
            return ship_to

        except:
            return None

    def get_price(self, soup):
        """Returns the price in dict or str/float/int"""
        try:
            price =  self.scraper.p_price(soup)
            if type(price) == str:
                price = price.replace('\t', '').replace('\n', '')

            return price
        except:
            return None

    @staticmethod
    def get_price_eur(price, file_date):
        """This function handles to conversion into euro's, this happens in three different ways:
        1. The price is already in euros, keep it that way
        2. The price is in dollars, will be converted to euro's via API (function: convert_usd_to_eur)
        3. The price is in bitcoin, bitcoin will be converted to dollars and dollars to euro's.
        The conversion rates of the given dates of the files are used for the conversion"""

        # Conversion for the pages that contain only one price
        if type(price) == str or type(price) == float or type(price) == int:
            if ('usd' in price.lower()) or ('$' in price.lower()):
                price_dollar = float(''.join(c for c in price if c.isdigit() or c == '.'))
                price_euro = float(Product.convert_usd_to_eur(price_dollar, file_date))
                if price_euro is not None:
                    price_euro = round(price_euro, 2)
                return price_euro
            if ('eur' in price.lower()) or ('€' in price):
                price_euro = float(''.join(c for c in price if c.isdigit() or c == '.'))
                if price_euro is not None:
                    price_euro = round(price_euro, 2)
                return price_euro
            if '฿' in price:
                if price is None:
                    return None
                price_bitcoin = float(''.join(c for c in price if c.isdigit() or c == '.'))
                price_dollar = Product.convert_btc_to_usd(price_bitcoin, file_date)
                if price_dollar is None:
                    return None
                price_dollar = round(float(price_dollar), 2)
                price_euro = Product.convert_usd_to_eur(price_dollar, file_date)
                if price_euro is None:
                    return None
                return round(float(price_euro), 2)

        # Conversion for the pages that contain multiple prices and are given in a dict
        if type(price) == dict:
            new_price_dict = {}
            for item in price:
                if ('usd' in price[item].lower()) or ('$' in price[item].lower()):
                    price_dollar = float(''.join(c for c in price[item] if c.isdigit() or c == '.'))
                    price_eur = Product.convert_usd_to_eur(price_dollar, file_date)
                    if price_eur is None:
                        new_price_dict[item] = None
                    else:
                        new_price_dict[item] = round(float(price_eur), 2)
                elif 'eur' in price[item].lower():
                    price_eur = float(''.join(c for c in price[item] if c.isdigit() or c == '.'))
                    if price_eur is  None:
                        new_price_dict[item] = None
                    else:
                        new_price_dict[item] = round(float(price_eur), 2)
                elif '฿' in price:
                    price_bitcoin = float(''.join(c for c in price[item] if c.isdigit() or c == '.'))
                    price_dollar = Product.convert_btc_to_usd(price_bitcoin, file_date)
                    if price_dollar is None:
                        new_price_dict[item] = None
                    else:
                        price_dollar = round(price_dollar, 2)
                        price_eur = Product.convert_usd_to_eur(price_dollar, file_date)
                        if price_eur is None:
                            new_price_dict[item] = None
                        else:
                            new_price_dict[item] = round(float(price_eur), 2)
                else:
                    new_price_dict[item] = None
            return new_price_dict

    def get_info(self, soup):
        """Returns the info as str"""
        try:
            return self.scraper.p_info(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_macro_category(self, soup):
        try:
            return self.scraper.p_macro_category(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_micro_category(self, soup):
        try:
            return self.scraper.p_micro_category(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_feedback(self, soup, file_date):
        """Returns the feedback on the product
        uses the feedback_handles to handle all feedback"""
        try:
            feedback_list = self.scraper.p_feedback(soup)
            return Product.feedback_handler(feedback_list, file_date)
        except:
            return None

    @staticmethod
    def feedback_handler(feedback_list, file_date):
        """Static method to export all the feedback
        Feedback_list is the list of given feedback.
        Returns the feedback list with appropriate formatted time"""
        for p, feedback in enumerate(feedback_list):
            if type(feedback['date']) == datetime.datetime:
                date = feedback['date'].date()
                # calculate the precision of the given time, this the possible deviation there is
                feedback_list[p]['date_deviation'] = Vendor.determine_date_deviation(feedback['date'])
                # Give the date in appropriate time format
                feedback_list[p]['date'] = time.mktime(date.timetuple())
            elif type(feedback['date']) == str:
                date = Vendor.calculate_time_since(feedback['date'], file_date)
                # calculate the precision of the given time, this the possible deviation there is
                feedback_list[p]['date_deviation'] = Vendor.determine_date_deviation(feedback['date'])
                # Give the date in appropriate time format
                feedback_list[p]['date'] = time.mktime(date.timetuple())
            else:
                # calculate the precision of the given time, this the possible deviation there is
                feedback_list[p]['date_deviation'] = None
                # Give the date in appropriate time format
                feedback_list[p]['date'] = None

        return feedback_list

    @staticmethod
    def get_country(abbreviation):
        """Return the right country when abbreviations were used. Returns the country as a string"""
        try:
            if abbreviation == 'ZZ':
                return 'Unspecified'
            else:
                return pycountry.countries.get(alpha_2=abbreviation).name
        except:
            return 'Country_naming_error'

    @staticmethod
    def convert_usd_to_eur(price, date):
        """Converts the price of dollar to eur on a specific date using an API"""
        date = datetime.datetime.fromtimestamp(date).date()  # convert unix to datetime
        if type(date) == datetime.date and (type(price) == float or type(price) == int):
            # two dates needed to find the exchange (USD/EUR) rate in that period
            date_2 = date - datetime.timedelta(days=-1)
            date_1 = date.strftime('%Y-%m-%d')
            date_2 = date_2.strftime('%Y-%m-%d')

            # Use the exchangeratesapi to find the right exchange rate
            response = requests.get(
                'https://api.exchangeratesapi.io/history?start_at=' + date_1 + '&end_at=' + date_2 + '&symbols=USD')
            try:
                if response.status_code != 200:
                    print('error: Request went wrong, exchangerates api status code: ' + str(response.status_code))
                    return None
                if response.status_code == 200:
                    if date_1 in response.json()['rates']:
                        conversion_rate = response.json()['rates'][date_1]['USD']
                    else:
                        conversion_rate = response.json()['rates'][date_2]['USD']

                    return price / conversion_rate
            except:
                try:
                    print('something went wrong with the exchangerates API')
                    print(response.status_code, response.json())
                    print(f'requested: {date_1} and {date_2}')
                    return None
                except:
                    print('something went wrong with the exchangerates API')
                    return None
        else:
            if type(date) != datetime.date:
                print('error: Wrong format of date, no datetime object')
            if type(price) != float:
                print('error: Wrong format of price, no float')

        return None

    @staticmethod
    def convert_btc_to_usd(price, date):
        """Converts the price of dollar to eur on a specific date using an API"""
        date = datetime.datetime.fromtimestamp(date).date()  # convert unix to datetime

        if type(date) == datetime.date and (type(price) == float or type(price) == int):
            # two dates needed to find the exchange (USD/EUR) rate in that period
            date = date.strftime('%Y-%m-%d')

            # Use the coindesk to find the right exchange rate
            response = requests.get(
                'https://api.coindesk.com/v1/bpi/historical/close.json?start=' + date + '&end=' + date)
            try:
                if response.status_code != 200:
                    print('error: Request went wrong, coindesk api status code: ' + str(response.status_code))
                    return None
                if response.status_code == 200:
                    conversion_rate = response.json()['bpi'][date]
                    return price * conversion_rate
            except:
                print('something went wrong with the coindesk API')
                return None

        else:
            if type(date) != datetime.date:
                print('error: Wrong format of date, no datetime object')
            if type(price) != float:
                print('error: Wrong format of price, no float')

        return None


class Vendor:
    """Scrape the soup for product"""

    def __init__(self, soup, scraper, file_date):
        self.scraper = scraper
        self.name = self.get_name(soup)
        self.score = self.get_score(soup)
        self.score_normalized = Vendor.get_score_normalized(self.score)
        # self.registration_extracted = self.get_registration(soup)
        registration_extracted = self.get_registration(soup)
        self.registration = Vendor.normalize_date(registration_extracted, file_date)
        self.registration_deviation = self.determine_date_deviation(registration_extracted)
        last_login_extracted = self.get_last_login(soup)
        # self.last_login_extracted = self.get_last_login(soup)
        self.last_login = Vendor.normalize_date(last_login_extracted, file_date)
        self.last_login_deviation = self.determine_date_deviation(last_login_extracted)
        self.sales = self.get_sales(soup)
        self.info = self.get_info(soup)
        self.pgp = self.get_pgp(soup)
        self.feedback = self.get_feedback(soup, file_date)

    def get_name(self, soup):
        """Returns the name of the vendor as a string"""
        try:
            return self.scraper.v_vendor_name(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_score(self, soup):
        """Returns the score of the Vendor"""
        try:
            score =  self.scraper.v_score(soup)
            # if type(score) == str:
            #     score = score.replace('\t', '').replace('\n', '')
            return score
        except:
            return None

    @staticmethod
    def get_score_normalized(score):
        """Returns the normalized score of the vendor"""

        if type(score) == tuple:  # Example: (1,5) means 1 point on scale up to 5
            return round(float(score[0]) / float(score[1]), 2)
        if type(score) == list:  # Example: [1,2] means 1 positive and 2 negatives
            if len(score) == 2:
                count = sum([abs(int(item)) for item in score])
                if count > 0:
                    score_normalized = 0.5 + (float(score[0])+float(score[1])/count)/2
                    return round(score_normalized, 2)
            if len(score) == 3:
                score = [abs(int(score[0])), abs(int(score[1])), abs(int(score[2]))]
                if sum(score) > 0:
                    score_normalized = (score[0] * 1 + score[1] * 0 + score[2] * 0.5) / sum(score)
                    return round(score_normalized, 2)

        return None

    def get_registration(self, soup):
        """Returns the registration date of the Vendor"""
        try:
            return self.scraper.v_registration(soup)
        except:
            return None

    def get_last_login(self, soup):
        """Returns the last login of the Vendor"""
        try:
            return self.scraper.v_last_login(soup)
        except:
            return None

    @staticmethod
    def normalize_date(date_to_normalize, file_creation_date):
        """Normalizes the date given the date to normalize and the file creation date"""
        try:
            # if the date is a datetime object, only keep the date
            if type(date_to_normalize) == datetime.datetime:
                date = date_to_normalize.date()
            # if the date is a string, the relative date needs to be calculated
            elif type(date_to_normalize) == str:
                date = Vendor.calculate_time_since(date_to_normalize, file_creation_date)
            else:
                date = None

            # return a unix time
            return time.mktime(date.timetuple())
        except:
            return None

    def get_sales(self, soup):
        """Returns the number of sales in int"""
        try:
            return int(self.scraper.v_sales(soup))
        except:
            return None

    def get_info(self, soup):
        """Returns the Vendor info as a string"""
        try:
            return self.scraper.v_info(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_pgp(self, soup):
        """Returns the PGP as a string"""
        try:
            return self.scraper.v_pgp(soup).replace('\t', '').replace('\n', '')
        except:
            return None

    def get_feedback(self, soup, file_date):
        """Returns the feedback"""
        try:
            feedback_list = self.scraper.v_feedback(soup)
            # use the Product.feedback_handler to adapt the time
            return Product.feedback_handler(feedback_list, file_date)
        except:
            return None

    @staticmethod
    def calculate_time_since(since, file_date):
        """Calculates the date in a timestamp
        since is the string with the relative date, mostly in this format: '2 months ago'
        file_date is the date of the file itself"""
        since = since.lower().split()
        timestamp = file_date
        time_since_unix = 0

        # add the time mentioned in the string to the unix time
        for p, item in enumerate(since):
            item = item.lower()
            value = since[p - 1].replace('~', '')
            if 'today' in item:
                return datetime.datetime.fromtimestamp(file_date).date()

            if 'years' in item:
                years = value
                time_since_unix += 31556926 * int(years)
            elif 'year' in item:
                time_since_unix += 31556926
            if 'months' in item:
                months = value
                time_since_unix += 2629743.83 * int(months)
            elif 'month' in item:
                time_since_unix += 2629743.83
            if 'weeks' in item:
                weeks = value
                time_since_unix += 604800 * int(weeks)
            elif 'week' in item:
                time_since_unix += 604800
            if 'days' in item:
                days = value
                time_since_unix += 86400 * int(days)
            elif 'day' in item:
                time_since_unix += 86400
        # calculate the relative time
        time_since = timestamp - time_since_unix
        return datetime.datetime.fromtimestamp(time_since).date()

    @staticmethod
    def determine_date_deviation(date):
        """Calculate the precision of the relative time.
        For example if the relative time was: 2 months ago, then the date is precise up to a month
        If it says 1 day ago, the precision is a day"""
        if type(date) == str:
            date = date.lower().split()
            length_idx = len(date) - 1
            while length_idx >= 0:
                if 'today' in date[length_idx].lower():
                    return 'day'
                if 'year' in date[length_idx].lower():
                    return 'year'
                if 'month' in date[length_idx].lower():
                    return 'month'
                if 'week' in date[length_idx].lower():
                    return 'week'
                if 'day' in date[length_idx].lower():
                    return 'day'
                if 'hour' in date[length_idx].lower():
                    return 'day'
                if 'minute' in date[length_idx].lower():
                    return 'day'
                if 'second' in date[length_idx].lower():
                    return 'day'

                length_idx -= 1
        if type(date) == datetime.date:
            return 'exact date'
        if type(date) == datetime.datetime:
            return 'exact date'


def json(file_input):
    """Export a json file for the input
    Can have two types of input:
    A string of the folder you want a json file of
    A list of paths to the files you want a json file of"""
    market_modules = import_market_modules()

    if type(file_input) == str:
        # find all html files in the subsequent folder
        file_list = open_folder(file_input)
    elif type(file_input) == list:
        file_list = file_input
    else:
        file_list = None

    data = extract_data(file_list, market_modules)

    json_list = []
    for page in data:
        if page['web_page'] is not None:
            web_page = page['web_page'].__dict__
            del web_page['soup']
            del web_page['file_name']
        else:
            web_page = None

        if page['page_data'] is not None:
            page_data = page['page_data'].__dict__
            del page_data['scraper']
        else:
            page_data = None

        json_format_data = {
            'web_page': web_page,
            'page_data': page_data}
        json_list.append(json_format_data)
    return json_list