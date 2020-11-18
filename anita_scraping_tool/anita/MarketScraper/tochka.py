def pagetype(soup):
    '''Define how to distinghuis vendor pages from product pages'''
    try:
        if soup.find_all('div', {'class': "ui segment"})[1].find_all('h3')[0].text == 'Purchase':
            return 'product'
    except:
        pass

    try:
        if soup.find('h3', {'class': "ui dividing header"}).text == 'About':
            return 'vendor'
    except:
        pass
    try:
        if soup.find('h3', {'class': "ui dividing header"}).text == 'Reviews':
            return 'vendor'
    except:
        pass


# -- PRODUCT CODE
def p_product_name(soup):
    title = soup.find('h2', {"ui dividing header"})
    for span in title('span'):
        span.decompose()
    return ' '.join(title.text.split())

def p_vendor(soup):
    return ' '.join(soup.find('div', {'class': "content card-header"}).text.split())[1:]

def p_ships_from(soup):
    return soup.find('table', {'class': "ui celled table fluid inverted green"}).find_all('span')[1].text

def p_ships_to(soup):
    return soup.find('table', {'class': "ui celled table fluid inverted green"}).find_all('span')[2].text

def p_price(soup):
    price_list = [' '.join(item.text.split()) for item in soup.find('table', {'ui very basic table'}).find_all('td')]
    i = 0
    price_dict = dict()
    while i < len(price_list):
        price_dict[price_list[i]] = price_list[i + 1]
        i += 2
    return price_dict

def p_info(soup):
    return soup.find('div', {'ui segment'}).text

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return None  # Not on website

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return None  # Not on website

# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    return ' '.join(soup.find('div', {'class': "content card-header"}).text.split())[1:]

def v_score(soup):
    """ Return the score of the vendor as float, or if multiple as float in list """
    return (float(soup.find('div', {'class' : 'ui label dark-green tiny'}).find('span').text),5)

def v_registration(soup):
    """ Return the moment of registration as datetime object """
    return ' '.join(soup.find_all('div', {'class' : 'date'})[0].text.split()[1:])

def v_last_login(soup):
    """ Return the moment of last login as datetime object"""
    return ' '.join(soup.find_all('div', {'class' : 'date'})[1].text.split()[2:])

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    return None  #no mention

def v_info(soup):
    """ Return the information as a string """
    # example: return soup.find('div', {'class' : 'container container_large'}).text
    return soup.find('div', {'class' : 'ui container'}).text

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    return None  # None found


# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []

    #loop to walk through the feedback
    if soup.find_all('a', {'class': 'item active'})[1].text.split()[0] == 'Reviews':
        for item in soup.find('div', {'class': 'ui comments'}).find_all('div', {'class':'comment'}):

            # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
            score  =  (item('span')[0].text.split()[0],5)

            # The message of the feedback in type str
            message =  item('pre')[0].text

            # The time in datetime object or time ago in type str
            date = item.find('span', {'class':'date'}).text

            # Name of the product that the feedback is about (if any) in type str
            product = None #not on website

            # User, name of the user or encrypted user name (if any) in type str
            user = item('a', {'class':'author'})[0].text[1:]

            # Deals by user (if any) in type int or str (if range)
            deals = None #not on website

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
    feedback_list = []

    #loop to walk through the feedback
    for item in soup.find('div', {'class', 'ui comments'}).find_all('div', {'class': 'comment'}):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (item.find('span').text.split()[0],5)

        # The message of the feedback in type str
        message = item.find('pre').text

        # The time in datetime object or time ago in type str
        date = item.find('span', {'class': 'date'}).text

        # User, name of the user or encrypted user name (if any) in type str
        user = item.find('a', {'class': 'author'}).text[1:]

        #in json format
        feedback_json = {
            'score' : score,
            'message' : message,
            'date' : date,
            'user' : user,
        }
        feedback_list.append(feedback_json)

    return feedback_list