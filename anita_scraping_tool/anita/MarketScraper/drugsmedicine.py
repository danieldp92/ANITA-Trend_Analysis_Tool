def pagetype(soup):
    """Define how to distinguish vendor pages from product pages"""
    try:
        if soup.find('div', {'class': "table_wrapper"}).find_all('th')[0].text == 'Item info:':
            return 'product'
    except:
        pass

    try:
        if soup.find('table', {'class': "msgtable"}).find('th').text == 'Vendor stats:':
            return 'vendor'
    except:
        pass


# -- PRODUCT CODE
def p_product_name(soup):
    return soup.find('div', {"content grid-8-12"}).find('h3').text

def p_vendor(soup):
    return soup.find('div', {'class': "table_wrapper"}).find('a').text

def p_ships_from(soup):
    return soup.find('div', {"table_wrapper"}).find_all('td')[3].text

def p_ships_to(soup):
    return soup.find('div', {"table_wrapper"}).find_all('td')[5].text

def p_price(soup):
    return soup.find('div', {'price_big_inner'}).text.split()[0]

def p_info(soup):
    return soup.find('div', {'prod_info'}).text

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return 'drugs'  # This website only sells drugs

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return soup.find('div', {"table_wrapper"}).find_all('td')[7].text.replace('\n','')

# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    return soup.find('h3').text

def v_score(soup):
    """ Return the score of the vendor in one of these two options:
    1. The score in a tuple as first item (float/int) and second item as the scale (float/int).
    Example: a 4.95 of scale up to 5: (4.95, 5), 97.7%: (97.7, 100)
    2. When the item consists of positives and negatives and possibly neutrals. [positive, negative, neutral]
    example: 96 negative, no neutrals, 20 positives: [20, 96, 0]
    """
    return (float(soup.find_all('td')[5].text.split('/')[0]),5)

def v_registration(soup):
    """ Return the moment of registration as datetime object """
    return soup.find_all('div',{'viewusercont'})[1].find_all('td')[1].text.replace(u'\xa0', u' ')

def v_last_login(soup):
    """ Return the moment of last login as datetime object"""
    return soup.find_all('div',{'viewusercont'})[1].find_all('td')[3].text.replace(u'\xa0', u' ')

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    return int(soup.find_all('td')[7].text)

def v_info(soup):
    """ Return the information as a string """
    return soup.find('div', {'class' : 'container container_large'}).text

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    pgp = soup.find('div', {'class', 'container container_large'}).find_all('p')
    for idx, text in enumerate(pgp):
        if '-----BEGIN PGP PUBLIC KEY BLOCK-----' in text:
            pgp_text = pgp[idx].text + pgp[idx + 1].text
    return pgp_text


# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors"""
    feedback_list = []

    # loop to walk through the feedback
    for item in soup.find_all('div', {'class': 'comment_wrapper'}):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (item.find('b').text.count('★'), 5)

        # The message of the feedback in type str
        message = item.find('p').text

        # The time in datetime object or time ago in type str
        date = ' '.join(item.find('span', {'class': 'commenttime'}).text.split())

        # Name of the product that the feedback is about (if any) in type str
        product = None  # Not on website

        # User, name of the user or encrypted user name (if any) in type str
        user = None  # Not on website

        # Deals by user (if any) in type int or str (if range)
        deals = None  # Not on website

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
    feedback_list = []

    # loop to walk through the feedback
    for item in soup.find_all('div', {'class': 'comment_wrapper'}):
        # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
        score = (item.find('b').text.count('★'), 5)

        # The message of the feedback in type str
        message = item.find('p').text

        # The time in datetime object or time ago in type str
        date = ' '.join(item.find('span', {'class': 'commenttime'}).text.split())

        # User, name of the user or encrypted user name (if any) in type str
        user = None  # Not on website

        # in json format
        feedback_json = {
            'score': score,
            'message': message,
            'date': date,
            'user': user,
        }
        feedback_list.append(feedback_json)

    return feedback_list