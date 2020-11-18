# ----------------------------------------------------------
# Marketscraper darkmarket
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
        if 'cart' in soup.find('div', {'class': 'col-md-7'}).text:
            return 'product'
    except:
        pass

    try:
        # example: if soup.find('table', {'class': "msgtable"}).find('th').text == 'Vendor stats:':
        if 'Vendor' in soup.find('ol', {'class': 'breadcrumb'}).text:
            return 'vendor'
    except:
        pass


# -- PRODUCT DATA
def p_product_name(soup):
    """ Return the name of the product as string """
    # example: return soup.find('div',{"content grid-8-12"}).find('h3').text
    return soup.find('div', {'class': 'col-md-5'}).find('h2').text


def p_vendor(soup):
    """Return the name of the vendor as string"""
    # example: return soup.find('div', {'class': "table_wrapper"}).find('a').text
    return soup.find('a', {'class': 'btn btn-light btn-sm'}).find('span').text


def p_ships_from(soup):
    """Return the place from where the package is delivered as string"""
    # example: return soup.find('div', {"table_wrapper"}).find_all('td')[3].text

    return None  # Not present


def p_ships_to(soup):
    """Return where the package can be delivered to as string
    If multiple; provide in a list"""

    return None  # Not present


def p_price(soup):
    """Return the price of the produc as string"""
    price_dict = dict()
    price_list = soup.find('div', {'class', 'col-md-12 text-center'}).find_all('li')
    for item in price_list:
        price_dict[item.text.replace('\n', '')] = item.find('strong').text.replace('\n', '')
    return price_dict


def p_info(soup):
    """Return the info as string"""
    # example: return soup.find('div', {'prod_info'}).text
    info = ''
    for string in soup.find('div', {'class': 'mt-4'}).find_all('p'):
        info = info + string.text
    return info


def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return soup.find('ol', {'class': 'breadcrumb'}).find_all('li')[1].text


def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    breadcrump = soup.find('ol', {'class': 'breadcrumb'}).find_all('li')
    if len(breadcrump) > 3:
        micro_category = soup.find('ol', {'class': 'breadcrumb'}).find_all('li')[3].text.replace('\n', '')
    else:
        micro_category = soup.find('ol', {'class': 'breadcrumb'}).find_all('li')[2].text.replace('\n', '')

    return micro_category


# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    # example: return soup.find('h3').text
    return soup.find('div', {'class': 'col-sm-5'}).find('a').text


def v_score(soup):
    """ Return the score of the vendor in one of these two options:
    1. The score in a tuple as first item (float/int) and second item as the scale (float/int).
    Example: a 4.95 of scale up to 5: (4.95, 5), 97.7%: (97.7, 100)
    2. When the item consists of positives and negatives and possibly neutrals. [positive, negative, neutral]
    example: 96 negative, no neutrals, 20 positives: [20, 96, 0]
    """
    s = soup.find('div', {'class': 'col-md-4 col-sm-6'}).find('span').text
    score = s[s.find("(") + 1:s.find(")")]
    return (score, 5)


def v_registration(soup):
    """ Return the moment of registration as datetime object """
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return parse('01' + soup.find_all('span', {'class': 'font-weight-semibold'})[1].text)


def v_last_login(soup):
    """ Return the moment of last login as datetime object, or as str when the time is a 'since'"""
    # example: return None # DRUGS MARKET ONLY HAS A SINCE
    return soup.find('a', {'class': 'btn btn-outline-info'}).text


def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    # example: return int(soup.find_all('td')[7].text)
    return None  # Non existent


def v_info(soup):
    """ Return the information as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return soup.find('div', {'class': 'col-sm-12'}).text


def v_pgp(soup):
    """ Return the pgp as a string"""
    pgp = soup.find("textarea").text
    return pgp.replace("\n", '')


# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""

    # There is feedback of vendors on this website. It is showed in a way that it is difficult to combine
    # the information.

    # feedback_list = []
    #
    # # loop to walk through the feedback
    # for review in soup.find('div', {'class': 'row mt-3'}).find('tbody').find_all('tr'):
    #
    #     score = None
    #     # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
    #     if review.find_all('td')[0].find('span').find('span', {'class': "fas fa-plus-circle text-success"}):
    #         score = 'positive'
    #     elif review.find_all('td')[0].find('span').find('span', {'class': "fas fa-minus-circle text-danger"}):
    #         score = 'negative'
    #     elif review.find_all('td')[0].find('span').find('span', {'class': "fas fa-stop-circle text-secondary"}):
    #         score = 'neutral'
    #
    #     # The message of the feedback in type str
    #     message = review.find_all('td')[0].find('span').text
    #
    #     # The time in datetime object or time ago in type str
    #     date = review.find_all('td')[2].text.replace('\n', '')
    #
    #     # Name of the product that the feedback is about (if any) in type str
    #     product = review.find_all('td')[0].find_all('span')[3].text
    #
    #     # User, name of the user or encrypted user name (if any) in type str
    #     user = review.find_all('td')[1].find('span').text.split('Buyer: ')[1].replace('\n', '')
    #
    #     # Deals by user (if any) in type int or str (if range)
    #     deals = None  # non existent
    #
    #     # in json format
    #     feedback_json = {
    #         'score': score,
    #         'message': message,
    #         'date': date,
    #         'product': product,
    #         'user': user,
    #         'deals': deals
    #     }
    #     feedback_list.append(feedback_json)
    #
    # return feedback_list
    return None


# -- PRODUCT FEEDBACK DATA
def p_feedback(soup):
    """ Return the feedback for the product"""
    feedback_list = []

    # loop to walk through the feedback
    for review in soup.find('table', {'class': 'table table-striped'}).find('tbody').find_all('tr'):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg
        # scores.
        score = (len(review.find_all('td')[0].find_all('i', {'class': 'fas fa-star'})), 5)

        # The message of the feedback in type str
        message = review.find_all('td')[3].text.replace('\n', '')

        # The time in datetime object or time ago in type str
        date = None  # non existent

        # User, name of the user or encrypted user name (if any) in type str
        user = None  # non existent

        # in json format
        feedback_json = {
            'score': score,
            'message': message,
            'date': date,
            'user': user,
        }
        feedback_list.append(feedback_json)

    return feedback_list
