# ----------------------------------------------------------
# This is a module that identifies markets
# To add a market, add an if statement.
# find a specific field in the page that uniquely identifies the market
# ----------------------------------------------------------

def identify_market(soup):
    # BERLUSCONI MARKET
    try:
        if soup.find('img', {'alt': "BERLUSCONI MARKET"}): #berlusconi image in page
            return 'berlusconi'
    except:
        pass

    # APOLLON MARKET
    try:
        if 'Apollon' in soup.find('span', {'class': 'bigger-90'}).text:
            return 'apollon'
    except:
        pass

    # AGARTHA MARKET
    try:
        if 'Agartha' in soup.find('div', {'id': 'page-heading'}).text:
            return 'agartha'
    except: pass

    # TOCHKA MARKET
    try:
        if 'Tochka' in soup.find_all('a', {'class': 'item'})[-1].text:
            return 'tochka'
    except:
        pass

    # DRUGSMEDICINE Market
    try:
        if soup.find('div', {'class': 'fix grid-3-12'}).find('img', {'id': 'logo_image'}):
            return 'drugsmedicine'
    except:
        pass

    # CANNAHOME Market
    try:
        if soup.find('img', {'alt': 'CannaHome'}): # If the image with this alt exists.
            return 'cannahome'
    except:
        pass

    # Silk Road 3.1
    try:
        if 'Silk Road 3' in soup.find('div', {'id': 'd'}).text:
            return 'silkroad3'
    except:
        pass

    # Empire Market
    try:
        if 'Empire Market' in soup.find('div', {'class': 'footer'}).text:
            return 'empiremarket'
    except:
        pass

    # SURFACE WEB: directdrugs
    try:
        if soup.find('div', {'class':'site-branding'}).find('img', {'alt':'DirectDrugs. Buy research drugs.'}):
            return 'directdrugs'
    except:
        pass

    # SURFACE WEB: drugscenter
    try:
        if soup.find('div', {'class': 'copyright-footer'}).find('strong').text == 'drugs-center.biz':
            return 'drugscenter'
    except:
        pass

    # SURFACE WEB: palmetto
    try:
        if soup.find('div', {'class': 'header'}).find('strong').text == 'Palmetto State Armory':
            return 'palmetto'
    except:
        pass

    # cannazon
    try:
        if 'cannazon' in soup.find('div', {'class': 'footer-bottom'}).text.lower():
            return 'cannazon'
    except:
        pass

    # darkmarket
    try:
        if soup.find('img', {'alt': 'DarkMarket'}):
            return 'darkmarket'
    except:
        pass







