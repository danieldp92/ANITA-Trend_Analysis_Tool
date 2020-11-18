# ----------------------------------------------------------
# This is a template for new markets
# Fill the indicated fields with answers, if you cannot
# find the specific field in the market. Let the function return None.
# ----------------------------------------------------------

# -- IMPORT
# from datetime import datetime
from dateutil.parser import parse


# -- MAIN PAGE DATA
def pagetype(soup):
    """Define the type of the page.
    Find a part in the page that indicates that the page is a vendor or product page. For example: 'item info' indicates
    that the page is about an item, thus a product page."""
    try:
        # example: if soup.find('div', {'class': "table_wrapper"}).find_all('th')[0].text == 'Item info:' :
        if soup.find('h2', {'class': 'title text-center'}).text == 'Product Details':
            return 'product'
    except:
        pass

    try:
        # example: if soup.find('table', {'class': "msgtable"}).find('th').text == 'Vendor stats:':
        if soup.find('h2', {'class': 'title text-center'}).text == 'Vendor Profile':
            return 'vendor'
    except:
        pass


# -- PRODUCT DATA
def p_product_name(soup):
    """ Return the name of the product as string """
    # example: return soup.find('div',{"content grid-8-12"}).find('h3').text
    return soup.find('div', {'class': 'product-information border-box container-box'}).find('h2').text


def p_vendor(soup):
    """Return the name of the vendor as string"""
    # example: return soup.find('div', {'class': "table_wrapper"}).find('a').text
    return list(soup.find('div', {'class':
                                      'product-information border-box container-box product-information-vendor'}).find(
        'a', {'class': 'vendor_rating'}).stripped_strings)[0]


def p_ships_from(soup):
    """Return the place from where the package is delivered as string"""
    # example: return soup.find('div', {"table_wrapper"}).find_all('td')[3].text
    ships_from = None
    data = list(
        soup.find('div', {'class':
                              'product-information border-box container-box product-information-vendor'}).find(
            'a', {'class': 'vendor_rating'}).stripped_strings)
    for idx, value in enumerate(data):
        if value == 'Shipping From:':
            ships_from = data[idx + 1].replace('\t', '').replace('\n', '').split('|')
            if len(ships_from) == 1:
                ships_from = ships_from[0]
    return ships_from


def p_ships_to(soup):
    """Return where the package can be delivered to as string
    If multiple; provide in a list"""
    # example: return soup.find('div', {"table_wrapper"}).find_all('td')[5].text
    country_list = None
    data = list(
        soup.find('div', {'class':
                              'product-information border-box container-box product-information-vendor'}).find(
            'a', {'class': 'vendor_rating'}).stripped_strings)
    for idx, value in enumerate(data):
        if value == 'Shipping To:':
            country_list = []
            string = data[idx + 1].split("|")
            for country in string:
                country = country.replace('\t', '').replace('\n', '')
                country_list.append(country)
    return country_list


def p_price(soup):
    """Return the price of the product as string"""
    # example: return soup.find('div', {'price_big_inner'}).text.split()[0]
    return soup.find('p', {'class' : 'price'}).text


def p_info(soup):
    """Return the info as string"""
    # example: return soup.find('div', {'prod_info'}).text
    info = ''
    for content in soup.find_all('div', {'class': 'content'})[:4]:
        info = info + content.text
    return info

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return 'drugs'  # Not on website but only drugs soldw

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return None  # Not on website


# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    # example: return soup.find('h3').text
    return soup.find('div', {'class': 'col-xs-12 vendor-box container-box'}).find('h2').text


def v_score(soup):
    """ Return the score of the vendor in one of these two options:
    1. The score in a tuple as first item (float/int) and second item as the scale (float/int).
    Example: a 4.95 of scale up to 5: (4.95, 5), 97.7%: (97.7, 100)
    2. When the item consists of positives and negatives and possibly neutrals. [positive, negative, neutral]
    example: 96 negative, no neutrals, 20 positives: [20, 96, 0]
    """
    pos = soup.find('span', {'class': 'badge badge-positive'}).text
    neg = soup.find('span', {'class': 'badge badge-negative'}).text
    return [pos, neg, 0]


def v_registration(soup):
    """ Return the moment of registration as datetime object """
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return parse(list(soup.find('div', {'class': 'col-xs-12 col-sm-6'}).stripped_strings)[1])


def v_last_login(soup):
    """ Return the moment of last login as datetime object, or as str when the time is a 'since'"""
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return None  # Non existent


def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    # example: return int(soup.find_all('td')[7].text)
    return int(list(soup.find('div', {'class': 'col-xs-12 col-sm-6'}).stripped_strings)[-1])


def v_info(soup):
    """ Return the information as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return soup.find_all('div', {'class': 'content'})[1].text + soup.find_all('div', {'class': 'content'})[2].text


def v_pgp(soup):
    """ Return the pgp as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return soup.find_all('div', {'class': 'content'})[3].text


# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []

    # loop to walk through the feedback
    for review in soup.find_all('div', {'class': 'row center-reviews'}):

        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg
        # scores.
        if review.find('span', {'class': 'badge badge-positive'}):
            score = 'positive'
        elif review.find('span', {'class': 'badge badge-negative'}):
            score = 'negative'
        else:
            score = None

        # The message of the feedback in type str
        message = list(review.find('div', {'class': 'col-xs-6'}).stripped_strings)[0]

        # The time in datetime object or time ago in type str
        date = parse(review.find('em').text)

        # Name of the product that the feedback is about (if any) in type str
        product = review.find('a').text

        # User, name of the user or encrypted user name (if any) in type str
        user = None  # Non existent

        # Deals by user (if any) in type int or str (if range)
        deals = None  # Non existent

        # in json format
        feedback_json = {
            'score': score,
            'message': message,
            'date': date,
            'product': product,
            'user': user,
            'deals': deals
        }
        feedback_list.append(feedback_json)

    return feedback_list


# # -- PRODUCT FEEDBACK DATA
# def p_feedback(soup):
#     """ Return the feedback for the product"""
#     feedback_list = []
#
#     # loop to walk through the feedback
#     for item in soup:
#         # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
#         score = None  # fill in
#
#         # The message of the feedback in type str
#         message = None  # fill in
#
#         # The time in datetime object or time ago in type str
#         date = None  # fill in
#
#         # User, name of the user or encrypted user name (if any) in type str
#         user = None  # fill in
#
#         # in json format
#         feedback_json = {
#             'score': score,
#             'message': message,
#             'date': date,
#             'user': user,
#         }
#         feedback_list.append(feedback_json)
#
#     return feedback_list
