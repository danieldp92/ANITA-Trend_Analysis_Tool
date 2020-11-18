# ----------------------------------------------------------
# This is the market scraper for silkroad3
# Fill the indicated fields with answers, if you cannot
# find the specific field in the market. Let the function return None.
# ----------------------------------------------------------

# -- IMPORT
from datetime import datetime


# -- MAIN PAGE DATA
def pagetype(soup):
    """Define the type of the page.
    Find a part in the page that indicates that the page is a vendor or product page. For example: 'item info' indicates
    that the page is about an item, thus a product page."""
    try:
        # example: if soup.find('div', {'class': "table_wrapper"}).find_all('th')[0].text == 'Item info:' :
        if soup.find('div', {'id': 'vp'}).find('h3').text == 'Place Order':  # you can only place an order if product
            return 'product'
    except:
        pass

    try:
        # example: if soup.find('table', {'class': "msgtable"}).find('th').text == 'Vendor stats:':
        if 'Last active' in soup.find('div', {'align': 'left'}).text:  # really difficult to find a tag for vendor
            return 'vendor'
    except:
        pass


# -- PRODUCT DATA
def p_product_name(soup):
    """ Return the name of the product as string """
    # example: return soup.find('div',{"content grid-8-12"}).find('h3').text
    return soup.find('div', {
        'style': 'text-align:center; font-size:16px; display:inline-block;color:#333;font-weight:bold'}).find('h3').text


def p_vendor(soup):
    """Return the name of the vendor as string"""
    # example: return soup.find('div', {'class': "table_wrapper"}).find('a').text
    return soup.find('div', {'style': 'color:#555;font-weight:bold;font-size:12px'}).find_all('a')[1].text


def p_ships_from(soup):
    """Return the place from where the package is delivered as string"""
    # example: return soup.find('div', {"table_wrapper"}).find_all('td')[3].text
    info = list(soup.find('div', {'style': 'color:#555;font-weight:bold;font-size:12px'}).stripped_strings)
    return info[info.index('Ships From:') + 1]


def p_ships_to(soup):
    """Return where the package can be delivered to as string
    If multiple; provide in a list"""
    # example: return soup.find('div', {"table_wrapper"}).find_all('td')[5].text
    return None  # None found


def p_price(soup):
    """Return the price of the produc as string"""
    # example: return soup.find('div', {'price_big_inner'}).text.split()[0]
    info = list(soup.find('div', {'style': 'color:#555;font-weight:bold;font-size:12px'}).stripped_strings)
    return info[info.index('Price:') + 1]


def p_info(soup):
    """Return the info as string"""
    # example: return soup.find('div', {'prod_info'}).text
    return soup.find_all('div', {'id': 'cats'})[1].text

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return None  # not on website

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return soup.find('div', {'style' : 'color:#555;font-weight:bold;font-size:12px'}).find_all('a')[-1].text

# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    # example: return soup.find('h3').text
    return list(soup.find('div', {'id' : 'cats'}).find('b').stripped_strings)[0]

def v_score(soup):
    """ Return the score of the vendor in one of these two options:
    1. The score in a tuple as first item (float/int) and second item as the scale (float/int).
    Example: a 4.95 of scale up to 5: (4.95, 5), 97.7%: (97.7, 100)
    2. When the item consists of positives and negatives and possibly neutrals. [positive, negative, neutral]
    example: 96 negative, no neutrals, 20 positives: [20, 96, 0]
    """
    pos = int(list(soup.find('div', {'id': 'cats'}).find('b').stripped_strings)[1])
    neg = abs(int(list(soup.find('div', {'id': 'cats'}).find('b').stripped_strings)[3]))

    return [pos, neg, 0]

def v_registration(soup):
    """ Return the moment of registration as datetime object """
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return None  # not found

def v_last_login(soup):
    """ Return the moment of last login as datetime object, or as str when the time is a 'since'"""
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return list(soup.find_all('div', {'align' : 'left'})[2].stripped_strings)[0] #messy

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    # example: return int(soup.find_all('td')[7].text)
    return None  # none found

def v_info(soup):
    """ Return the information as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return ' '.join(list(soup.find_all('div', {'align' : 'left'})[2].stripped_strings)[1:])

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    return None  # NONE FOUND!

# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []

    #loop to walk through the feedback
    for review in soup.find_all('div', {'align': 'left'})[4].find_all('div', {'id': 'cats'})[1:]:

        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (float(list(review.find('div').stripped_strings)[0].split('/')[0]),
                 float(list(review.find('div').stripped_strings)[0].split('/')[1]))
        # The message of the feedback in type str
        message = review.find_all('span')[2].text
        if message == 'No feedback.':
            message = None

        # The time in datetime object or time ago in type str
        date = list(review.find('span').stripped_strings)[-1].split(')')[1]

        # Name of the product that the feedback is about (if any) in type str
        product = list(review.find('span').stripped_strings)[4]

        # User, name of the user or encrypted user name (if any) in type str
        user = list(review.find('span').stripped_strings)[1]

        # Deals by user (if any) in type int or str (if range)
        deals = None #not existing


        #in json format
        feedback_json = {
            'score' : score,
            'message' : message,
            'date' : date,
            'product' : product,
            'user' : user,
            'deals' : deals
        }
        feedback_list.append(feedback_json)

    return feedback_list

#-- PRODUCT FEEDBACK DATA
def p_feedback(soup):
    """ Return the feedback for the product"""
    feedback_list = []

    #loop to walk through the feedback
    for review in soup.find('div', {'style': 'padding:0px; margin-bottom:10px; font-size:12px;'}).find_all('div', {
        'id': 'cats'}):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (float(list(review.find('div').stripped_strings)[0].split('/')[0]),
                 float(list(review.find('div').stripped_strings)[0].split('/')[1]))

        # The message of the feedback in type str
        message = review.find('span').text
        if message == 'No feedback.':
            message = None

        # The time in datetime object or time ago in type str
        date = list(review.stripped_strings)[4].split(')')[1]  # bit messy

        # User, name of the user or encrypted user name (if any) in type str
        user = list(review.stripped_strings)[1]

        #in json format
        feedback_json = {
            'score' : score,
            'message' : message,
            'date' : date,
            'user' : user,
        }
        feedback_list.append(feedback_json)

    return feedback_list




