'''This is the specific file for the Berlusconi market that will be used by the main scraper'''
from datetime import datetime

def pagetype(soup):
    '''Define how to distinghuis vendor pages from product pages'''
    try:
        if soup.find('button', {'class': "btn btn-block btn-danger btn-lg"}).text == ' Buy Now ':
            return 'product'
    except:
        pass

    try:
        if soup.find('span', {'class': "label label-primary"}).text == 'Vendor':
            return 'vendor'
    except:
        pass

#-- PRODUCT CODE
def p_product_name(soup):
    '''Returns the name of the product'''
    return soup.find('ol',{'class':'breadcrumb'}).find_all('li')[3].text

def p_vendor(soup):
    '''Returns the username from the Berlusconi market'''
    return str(soup.select("a[href*=vendor]")[0].text.strip())

def p_ships_from(soup):
    '''Returns where the product ships from'''
    if soup.find('div',{'class':'col-sm-7'}).find_all('td')[3].text == 'Physical':
        return soup.find('div',{'class':'col-sm-7'}).find_all('td')[7].text
    else:
        return None

def p_ships_to(soup):
    '''Returns where the product ships to'''
    if soup.find('div',{'class':'col-sm-7'}).find_all('td')[3].text == 'Physical':
        location =  soup.find('div',{'class':'col-sm-7'}).find_all('td')[9].text
        if 'Worldwide shipping' in location:
            return ['Worldwide']
        if 'Worldwide' in location:
            return ['Worldwide']
        if 'countries' in location:
            return ['Worldwide']
        else:
            return location.replace(' ','').split(',')
    return None

def p_price(soup):
    '''Returns the price from the Berlusconi market'''
    return str(soup.find('div',{"class":"listing-price"}).strong.text)#[:-5]

def p_info(soup):
    '''Returns the description from the product'''
    #return ''.join(soup.find('p').text)
    if soup.find_all('li', {'class' : 'active'})[2].text == 'Details':
        return ''.join(soup.find('p').text)

def p_macro_category(soup):
    """Return a macro category, for example: drugs, weapons, other"""
    return soup.find('ol', {'class' : 'breadcrumb'}).find_all('li')[1].text

def p_micro_category(soup):
    """Return a micro category, for example: cannabis, cocaine"""
    return soup.find('ol', {'class' : 'breadcrumb'}).find_all('li')[2].text
# -- VENDOR DATA
def v_vendor_name(soup):
    """ Return the name of the vendor as string """
    return soup.find('h1').text.strip().split()[0]

def v_score(soup):
    """ Return the score of the vendor as float, or if multiple as float in list """
    # example: return soup.find_all('td')[5].text
    positive = str(soup.find("strong", {"style": "font-size:15px;"}).text)
    neutral = soup.find_all("strong", {"style": "font-size:15px;"})[1].text
    negative = soup.find_all("strong", {"style": "font-size:15px;"})[2].text
    return [positive,negative,neutral]

def v_registration(soup):
    """ Return the moment of registration as datetime object """
    date = str(soup.find("i", {"class": "fa-user"}).next_sibling.strip()[15:25])
    return datetime.strptime(date, "%Y-%m-%d")  # .strftime("%d/%m/%Y")

def v_last_login(soup):
    """ Return the moment of last login as datetime object"""
    date = str(soup.find("i", {"class": "fa-feed"}).next_sibling.strip()[12:22])
    return datetime.strptime(date, "%Y-%m-%d")#.strftime("%d/%m/%Y")

def v_sales(soup):
    """ Return the number of sales, also known as transactions or orders as int """
    return int(soup.find("strong",{"style":"font-size:15px;"}).text)

def v_info(soup):
    """ Return the information as a string """
    if soup.find_all('li', {'class' : 'active'})[2].text == 'Profile':
        return soup.find_all('div',{'class':'row'})[2].find_all('p')[10].text
    return None

def v_pgp(soup):
    """ Returns the pgp as a string """
    # example: if soup.find('a', {'class': 'tablinks focus'}).text == 'PGP': soup.find('pre',
    # {'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
    if soup.find_all('li', {'class', 'active'})[2].text == 'PGP':
        return soup.find_all('div', {'class', 'row'})[1].find_all('p')[10].text
    else:
        return None


# -- VENDOR FEEDBACK DATA
def v_feedback(soup):
    """ Return the feedback for the vendors """
    feedback_list = []
    if soup.find_all('li', {'class' : 'active'})[2].text == 'Feedback':
        #loop to walk through the feedback, thus create a list of all feedback
        for item in soup.find('tbody').find_all('tr'):

            # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
            if item.find_all('td')[0].find_all('i', {'class':"fa fa-thumbs-o-up"}):
                score = 'positive'
            elif item.find_all('td')[0].find_all('i', {'class':"fa fa-thumbs-o-down"}):
                score = 'negative'
            else:
                score = 'error'

            # The message of the feedback in type str
            message =  item.find_all('td')[1].text

            # The time in datetime object or time ago in type str
            date = datetime.strptime(item.find_all('td')[3].text[:-4], "%Y-%m-%d %H:%M:%S")

            # Name of the product that the feedback is about (if any) in type str
            product = None #fill in

            # User, name of the user or encrypted user name (if any) in type str
            user = item('td')[2].text.split()[0]

            # Deals by user (if any) in type int or str (if range)
            deals = int(item('td')[2].text.split()[1][1:-1])


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
    if 'No feedbacks yet' not in soup.find('div', {'class': 'col-md-12'}).text:
        feedback_list = []

        # loop to walk through the feedback
        for item in soup.find('div', {'class': 'col-md-12'}).find_all('tr')[1:]:
            # Find the score, can be numerical score: (score, scale), or 'positive', 'negative' or 'neutral' for pos/neg scores.
            if item.find_all('td')[0].find_all('i', {'class': "fa fa-thumbs-o-up"}):
                score = 'positive'
            elif item.find_all('td')[0].find_all('i', {'class': "fa fa-thumbs-o-down"}):
                score = 'negative'
            elif item.find_all('td')[0].find_all('i', {'class': "fa fa-circle-o"}):
                score = 'neutral'
            else:
                score = None

            # The message of the feedback in type str
            message = item.find_all('td')[1].text

            # The time in datetime object or time ago in type str
            date = datetime.strptime(item.find_all('td')[3].text[:-4], "%Y-%m-%d %H:%M:%S")

            # User, name of the user or encrypted user name (if any) in type str
            user = item.find_all('td')[2].text[:-5]

            # in json format
            feedback_json = {
                'score': score,
                'message': message,
                'date': date,
                'user': user,
            }
            feedback_list.append(feedback_json)
    else:
        feedback_list = None

    return feedback_list