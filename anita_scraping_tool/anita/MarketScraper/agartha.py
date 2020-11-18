# -- IMPORT
from datetime import datetime

# -- MAIN PAGE DATA
def pagetype(soup):
    '''Define how to distinghuis vendor pages from product pages'''
    try:
        if soup.find_all('a', {'class' : 'btn btn-link btn-xs'})[1].text == 'Listings':
            return 'product'
    except:
        pass

    try:
        if soup.find('span', {'class' : 'user-class-hint'}).find('strong').text == 'Vendor':
            return 'vendor'
    except:
        pass


#-- PRODUCT CODE
def p_product_name(soup):
    return soup.find('h2').text

def p_vendor(soup):
    return soup.find('div', {'class' : 'panel-body'}).find('a').text

def p_ships_from(soup):
    for item in soup.find_all('p'):
        if 'Ships From: ' in item.text:
            ship_from = item
            for b in ship_from('b'):
                b.decompose()
            return ' '.join(ship_from.text.split())

def p_ships_to(soup):
    for item in soup.find_all('p'):
        if 'Ships To: ' in item.text:
            ship_from = item
            for b in ship_from('b'):
                b.decompose()
            return ship_from.text.split()[0]

def p_price(soup):
    return ' '.join(soup.find('span', {'style' : 'font-size:95%;'}).text.split()[1:3])

def p_info(soup):
    return soup.find('p', {'style' : 'max-width:74%; width:auto; overflow:auto; word-wrap: break-word; text-overflow: ellipsis;'}).text

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return None  # Not on website

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    item = soup.find('div', {'class': 'panel-body'}).find('p').text
    if 'category' in item.lower():
        micro_category = item.split(': ')[1].lower()
    elif soup.find('p', {'class' : 'c'}):
            micro_category = soup.find('p', {'class' : 'c'}).find('b').text.lower()
    else:
        micro_category = None
    if micro_category == '':
        micro_category = None
    return micro_category

# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    return soup.find_all('a', {'class' : 'btn btn-link btn-xs'})[1].text

def v_score(soup):
    """ Return the score of the vendor as float, or if multiple as float in list """
    return (float(soup.find('span', {'class' : 'gen-user-ratings'}).text.split()[1]), 100)

def v_registration(soup):
    """ Return the moment of registration as datetime object """
    time = soup.find_all('div', {'class': 'vendorbio-stats-online'})[0]
    for item in time('span'):
        item.decompose()
    return ' '.join(time.text.split()).split('.')[0]

def v_last_login(soup):
    """ Return the moment of last login as datetime object"""
    time = soup.find_all('div', {'class': 'vendorbio-stats-online'})[0]
    for item in time('span'):
        item.decompose()
    return ' '.join(time.text.split()).split('.')[1]

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    return ' '.join(soup.find_all('span', {'class' : 'gen-user-ratings'})[1].text.split()[2:3])

def v_info(soup):
    """ Return the information as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return soup.find('p', {'style' : 'word-wrap: break-word; text-overflow: ellipsis;'}).text

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    return soup.find('pre', {'class' : 'small pre-scrollable pgpkeytoken'}).text

# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []

    #loop to walk through the feedback
    for item in soup.find('div', {'class': 'embedded-feedback-list'}).find('tbody').find_all('tr'):

        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score  =  (int(item('td')[0].text[0]),5)

        # The message of the feedback in type str
        message =  item('td')[1].text

        # The time in datetime object or time ago in type str
        date = item('td')[3].text

        # Name of the product that the feedback is about (if any) in type str
        product = ' '.join(item('td')[2].text.split())

        # User, name of the user or encrypted user name (if any) in type str
        user = item('td')[4].text.split()[0]

        # Deals by user (if any) in type int or str (if range)
        deals = ' '.join(item('td')[4].text.split()[-4:])


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

# -- PRODUCT FEEDBACK DATA
def p_feedback(soup):
    """ Return the feedback for the product"""
    """ NONE IN DATASET, THUS ALL NONE"""
    feedback_list = []

    # loop to walk through the feedback
    for item in soup.find('div', {'class': 'embedded-feedback-list'}).find('tbody').find_all('tr'):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (int(item('td')[0].text[0]), 5)

        # The message of the feedback in type str
        message = item('td')[1].text

        # The time in datetime object or time ago in type str
        date = item('td')[2].text

        # User, name of the user or encrypted user name (if any) in type str
        user = item('td')[3].text.split()[0]

        # in json format
        feedback_json = {
            'score': score,
            'message': message,
            'date': date,
            'user': user,
        }
        feedback_list.append(feedback_json)

    return feedback_list


