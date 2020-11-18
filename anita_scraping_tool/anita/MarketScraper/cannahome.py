# ----------------------------------------------------------
# This is the market scraper for cannahome
# Fill the indicated fields with answers, if you cannot
# find the specific field in the market. Let the function return None.
# ----------------------------------------------------------

# -- IMPORT
from dateutil.parser import parse


# -- MAIN PAGE DATA
def pagetype(soup):
    """Define the type of the page.
    Find a part in the page that indicates that the page is a vendor or product page. For example: 'item info' indicates
    that the page is about an item, thus a product page."""
    try:
        # example: if soup.find('div', {'class': "table_wrapper"}).find_all('th')[0].text == 'Item info:' :
        if soup.find('a', {'class': 'btn big wide'}).text == ' Order Product':
            return 'product'
        else:
            pass
    except:
        pass

    try:
        # example: if soup.find('table', {'class': "msgtable"}).find('th').text == 'Vendor stats:':
        if soup.find('a', {'class': 'btn wide purple arrow-right'}).text == "View All Vendor's Listings":
            return 'vendor'
        else:
            pass
    except:
        pass


# -- PRODUCT DATA
def p_product_name(soup):
    """ Return the name of the product as string """
    return soup.find('div', {"row"}).find('h2').text


def p_vendor(soup):
    """Return the name of the vendor as string"""
    return soup.find('div', {'class': "row rows-20"}).find('div', {'class': 'row'}).find('a').text


def p_ships_from(soup):
    """Return the place from where the package is delivered as string"""
    return soup.find_all('div', {'class': "row cols-15"})[1].find_all('label')[1].text


def p_ships_to(soup):
    """Return where the package can be delivered to as string
    If multiple; provide in a list"""
    # no examples to learn from
    return None  # replace None


def p_price(soup):
    """Return the price of the produc as string"""
    return soup.find('div', {'class': "price"}).find('span', {'class': 'big'}).text.split(' ')[0]


def p_info(soup):
    """Return the info as string"""
    return soup.find('div', {'class': 'top-tabs'}).find('div', {'class': "formatted"}).text

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return 'drugs'  # Not on Website, but only drugs sold

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return None  # Not on website

# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    return soup.find('div', {'class' : 'main-infos'}).find('h2').text

def v_score(soup):
    """ Return the score of the vendor in one of these two options:
    1. The score in a tuple as first item (float/int) and second item as the scale (float/int).
    Example: a 4.95 of scale up to 5: (4.95, 5), 97.7%: (97.7, 100)
    2. When the item consists of positives and negatives and possibly neutrals. [positive, negative, neutral]
    example: 96 negative, no neutrals, 20 positives: [20, 96, 0]
    """
    s = soup.find('div', {'class': 'main-infos'}).find('div', {'class': 'rating stars color-yellow'}).text
    return (float(s[s.find("[") + 1:s.find("]")]), 5)


def v_registration(soup):
    """ Return the moment of registration as datetime object """
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return None  # Not present on site

def v_last_login(soup):
    """ Return the moment of last login as datetime object, or as str when the time is a 'since'"""
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return soup.find('div', {'class': 'corner'}).find('div', {'class' : 'aux'}).text  #returns a string

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    # example: return int(soup.find_all('td')[7].text)
    return None  # not available

def v_info(soup):
    """ Return the information as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return soup.find('div', {'class' : 'contents'}).text

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    return soup.find_all('textarea')[1].text

# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []

    #loop to walk through the feedback
    for review in soup.find('ul', {'class' : 'row list-ratings columns'}).find_all('li'):

        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (len(review.find('div', {'class': 'rating stars color-yellow'}).find_all('i', {'class': 'full'})), 5)

        # The message of the feedback in type str
        message = review.find('div', {'class': 'right formatted'}).text

        # The time in datetime object or time ago in type str
        date = parse(review.find('date').text)

        # Name of the product that the feedback is about (if any) in type str
        product = review.find('small').text

        # User, name of the user or encrypted user name (if any) in type str
        user = None # not present

        # Deals by user (if any) in type int or str (if range)
        deals = None # not present

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

    # loop to walk through the feedback
    for review in soup.find_all('div', {'class': "col-5"})[2].find_all('li'):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg
        # scores.
        score = (int(len(review.find_all('i', {'class': 'full'}))), 5)

        # The message of the feedback in type str
        message = review.find('div', {'class': 'right formatted'}).text

        # The time in datetime object or time ago in type str
        date = parse(review.find('date').text)

        # User, name of the user or encrypted user name (if any) in type str
        user = None  # not available

        # in json format
        feedback_json = {
            'score': score,
            'message': message,
            'date': date,
            'user': user,
        }
        feedback_list.append(feedback_json)

    return feedback_list
