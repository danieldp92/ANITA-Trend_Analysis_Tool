# -- IMPORT
from datetime import datetime

# -- MAIN PAGE DATA
def pagetype(soup):
    '''Define how to distinghuis vendor pages from product pages'''
    try:
        if soup.find('h3').text == 'Item For Sale : ' :
            return 'product'
    except:
        pass

    try:
        if soup.find('h3').text == 'User Profile : ':
            return 'vendor'
    except:
        pass


#-- PRODUCT CODE
def p_product_name(soup):
    return soup.find('div', {'class' : 'col-sm-12'}).find('a').text

def p_vendor(soup):
    return soup.find_all('div', {'class' : 'col-sm-12'})[1].find('small').find('b').text.split('(')[0][:-1]

def p_ships_from(soup):
    ship_from = soup.find_all('div', {'class': 'col-sm-12'})[1].find_all('small')[12]
    for item in ship_from('b'):
        item.decompose()
    return ship_from.text[1:-1]

def p_ships_to(soup):
    return soup.find_all('div', {'class' : 'col-sm-12'})[1].find_all('small')[14].text[1:-1]

def p_price(soup):
    return ' '.join(soup.find('span', {'class' : 'label label-info'}).text.split(' ')[3:5])

def p_info(soup):
    if soup.find('li', {'class': 'active'}).text == 'Product Description':
        return soup.find('pre').text

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return None  # Not in website

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return None  # Not in website

# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    return soup.find('div', {'class' : 'col-sm-12'}).find('small').find('b').text.split('(')[0][:-1]

def v_score(soup):
    """ Return the score of the vendor as float, or if multiple as float in list """
    score = soup.find('div', {'class': 'col-sm-5'}).find_all('span')[4]
    for item in score('b'):
        item.decompose()
    return (int(score.text[1:-2]),100)

def v_registration(soup):
    """ Return the moment of registration as datetime object """
    date = soup.find('div', {'class': 'col-sm-5'}).find_all('span')[5]
    for item in date('b'):
        item.decompose()
    date_string = date.text
    return datetime.strptime(date_string, "%b %d, %Y")

def v_last_login(soup):
    """ Return the moment of last login as datetime object"""
    date = soup.find('div', {'class': 'col-sm-5'}).find_all('span')[6]
    for item in date('b'):
        item.decompose()
    date_string = date.text
    return datetime.strptime(date_string, "%b %d, %Y")

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    sales = soup.find('div', {'class': 'col-sm-2'}).find_all('span')[0]
    for item in sales('b'):
        item.decompose()
    return sales.text

def v_info(soup):
    """ Return the information as a string """
    if soup.find('li', {'class': 'active'}).text == 'Profile':
        return soup.find_all('div', {'class' : 'panel panel-default'})[5].text

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    if soup.find('li', {'class', 'active'}).text == 'PGP Public Key':
        pgp = soup.find_all('div', {'class', 'col-sm-5'})[1].text
        return pgp
    else:
        return None

# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []
    if soup.find('li', {'class': 'active'}).text in ['Positive Feedback', 'Negative Feedback', 'Neutral Feedback']:

        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        if soup.find('li', {'class': 'active'}).text == 'Positive Feedback':
            score = 'positive'
        elif soup.find('li', {'class': 'active'}).text == 'Negative Feedback':
            score = 'negative'
        elif soup.find('li', {'class': 'active'}).text == 'Neutral Feedback':
            score = 'neutral'
        else:
            score = None

        # loop to walk through the feedback
        for item in soup.find('tbody').find_all('tr'):

            # The message of the feedback in type str
            message = item('td')[1]('small')[0].text

            # The time in datetime object or time ago in type str
            time_line = item('td')[4]
            for a in time_line('a'):
                a.decompose()
            date = datetime.strptime(time_line.text, "%b %d, %Y %H:%M")

            # Name of the product that the feedback is about (if any) in type str
            product_line = item('td')[1]
            for small in product_line('small'):
                small.decompose()
            product = product_line.text

            # User, name of the user or encrypted user name (if any) in type str
            user = item('td')[2].text

            # Deals by user (if any) in type int or str (if range)
            deals = None  # not present in this site

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

# -- PRODUCT FEEDBACK DATA
def p_feedback(soup):
    """ Return the feedback for the product"""

    #loop to walk through the feedback
    feedback_list = []
    if soup.find('li', {'class': 'active'}).text == 'Feedback':
        for item in soup.find('div', {'class': 'table-responsive'}).find('tbody').find('tbody').find_all('tr'):

            # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
            score_line = item.find_all('td')[0].text
            if score_line == '☒':
                score = 'negative'
            elif score_line == '☑':
                score = 'positive'
            else:
                score = None

            # The message of the feedback in type str
            message = item.find_all('td')[1].small.text

            # The time in datetime object or time ago in type str
            time_line = item.find_all('td')[4]
            for a in time_line('a'):
                a.decompose()
            date = datetime.strptime(time_line.text, "%b %d, %Y %H:%M")

            # User, name of the user or encrypted user name (if any) in type str
            user = item.find_all('td')[2].text

            #in json format
            feedback_json = {
                'score' : score,
                'message' : message,
                'date' : date,
                'user' : user,
            }
            feedback_list.append(feedback_json)
    else:
        feedback_list = None

    return feedback_list