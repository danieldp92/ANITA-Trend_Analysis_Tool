"""
Merge
This module is part of ANITA

This module contains functions for the merging of new files with the current existing files
This is done in two phases:
A. Merging the files created by the scraper. Combining html files that contain the same information to one product
or vendor json file
B. Merging the product and vendor files with the existing data
"""

import datetime
import os
import json
import time
from .ImportFile import create_date_folder, create_market_folder


def extract_time(feedback_json):
    """Helper function for the merge_items function"""
    if feedback_json['date'] is not None:
        return int(feedback_json['date'])
    else:
        return None


def merge_items(json_list):
    """
    Merges the pages together. Multiple HTML files can contain information about one vendor or product. This function
    merges them together and returns no duplicates.
    :param json_list: list of json files created by anita.scraper package
    :return: list of merged items in same format
    """

    # initialize
    merged_dict = {}

    # loop through all the pages in the json_list
    for page in json_list:
        # date needed in yyyy_mm_dd format
        date = datetime.datetime.fromtimestamp(page['web_page']['date']).date().strftime('%Y_%m_%d')
        # create an item_id that contains the name and the market
        try:
            if page['web_page']['page_type'] == 'product':
                if page['page_data']['vendor'] is not None:
                    item_id = page['page_data']['name'] + ' || ' + page['page_data']['vendor'] + ' || ' + page[
                        'web_page']['market'] + '||' + date
                else:
                    item_id = page['page_data']['name'] + ' || ' + page['web_page']['market'] + '||' + date
            elif page['web_page']['page_type'] == 'vendor':
                item_id = page['page_data']['name'] + ' || ' + page['web_page']['market'] + '||' + date
            else:
                continue
        except:
            continue

        # check whether the item is not already in the merged dict
        if item_id not in merged_dict:
            # add the item to the dict
            merged_dict[item_id] = {'web_page': page['web_page'], 'page_data': page['page_data']}
        # if the item_id is already in the list, check per key whether something needs to be added
        else:
            # check for all keys, except feedback
            keys = list(page['page_data'].keys())
            if 'feedback' in keys:
                keys.remove('feedback')
            for key in keys:
                if page['page_data'][key] is not None:
                    if merged_dict[item_id]['page_data'][key] is None:
                        merged_dict[item_id]['page_data'][key] = page['page_data'][key]

            # check for feedback separately
            # if not page['page_data']['feedback']:
            #     page['page_data']['feedback'] = None
            # if not merged_dict[item_id]['page_data']['feedback']:
            #     merged_dict[item_id]['page_data']['feedback'] = None

            if page['page_data']['feedback'] is not None:
                if merged_dict[item_id]['page_data']['feedback'] is None:
                    merged_dict[item_id]['page_data']['feedback'] = page['page_data']['feedback']
                else:  # merged_dict[item_id]['page_data']['feedback'] is not None:
                    for feedback in page['page_data']['feedback']:
                        if feedback not in merged_dict[item_id]['page_data']['feedback']:
                            merged_dict[item_id]['page_data']['feedback'].append(feedback)

    # Sort the feedback on date (oldest first)
    for item_id in merged_dict:
        if merged_dict[item_id]['page_data']['feedback'] is not None:
            if merged_dict[item_id]['page_data']['feedback'] != []:
                if merged_dict[item_id]['page_data']['feedback'][0]['date'] is not None:
                    merged_dict[item_id]['page_data']['feedback'].sort(key=extract_time, reverse=False)

    # sort merged_dict on date (oldest first)
    merged_dict = {k: v for k, v in
                   sorted(merged_dict.items(), key=lambda item: item[1]['web_page']['date'], reverse=False)}

    return merged_dict


def merge_json_product(json_list):
    """
    :param json_list: list of json files created by anita.scraper package
    :return: list of merged items in same format, only containing the vendor pages
    """
    return merge_items([page for page in json_list if page['web_page']['page_type'] == 'product'])


def merge_json_vendor(json_list):
    """
    :param json_list: list of json files created by anita.scraper package
    :return: list of merged items in same format, only containing the vendor pages
    """
    return merge_items([page for page in json_list if page['web_page']['page_type'] == 'vendor'])


def retrieve_market_and_date(data):
    """
    Takes in the data of one specific page and returns the date, market, name and page_type from the json format
    :param data: data of a vendor or product in json format
    :return: date: str, market: str, name: str, page_type: str ('Vendor' or 'Product')
    """
    date = data['web_page']['date']
    market = data['web_page']['market']
    name = data['page_data']['name']
    page_type = data['web_page']['page_type']
    return date, market, name, page_type


def retrieve_name(data):
    """
    Takes in the data of one specific page and returns the name
    :param data: data of a vendor or product in json format
    :return: name: str, name of the vendor or product
    """
    return data['page_data']['name']


def retrieve_reviews(data):
    """
    Takes in data of one specific page and returns a list of 5 older reviews
    :param data: ata of a page in json format
    :return: None or list, list with 5 oldest feedback of the page
    """

    feedback = data['page_data']['feedback']
    if feedback is None:
        return None
    else:
        last_feedback = feedback[-5:]  # gets the last 5 feedback
        return last_feedback


def export_new_json(file_path, page_data, item_id):
    """
    This function creates a new json file on the location given by param file_path
    :param file_path: str, the path were the new file needs to be create
    :param page_data: json, information of the data
    :param item_id: str, ID of the product or Vendor
    """
    with open(file_path, 'w') as outfile:
        json.dump({item_id: page_data}, outfile, default=myconverter)


def myconverter(o):
    """
    JSON cannot store datetime objects, thus unix time is used
    """
    if isinstance(o, datetime.date):
        return time.mktime(o.timetuple())


def find_existing_json(json_export_folder, market, date, page_type):
    """
    Finds the most recent export of the JSON file for the given market and type
    :param json_export_folder: str, path where all json files are stored
    :param market: str, name of the market
    :param date: int (unix), the creation date of the product/vendor where a previous version is needed
    :param page_type: str (vendor or product), type of the page
    :return: str (path) or False, returns the Path of the previous JSON file or False if None could be found
    """
    # Search in the folder of the market of the file
    path = json_export_folder + market

    # Make a list of all json files
    export_dates = sorted([os.path.join(root, name).split('/')[-2]
                           for root, dirs, files in os.walk(path)
                           for name in files
                           if name.endswith((page_type + ".txt", ".json"))])

    # find the date of the most recent export compared to the current
    if date not in export_dates:
        export_dates.append(date)
    idx = export_dates.index(date) - 1
    if idx >= 0:
        # return the most recent (previous) file
        path = path + '/' + export_dates[idx] + '/' + export_dates[idx] + '_' + market + '_' + page_type + '.txt'
        return path
    # If none could be found, return False
    return False


def add_to_existing_json(file_path, page_data, item_id):
    """
    Adds the data to an existing JSON file
    :param file_path: str, the path of the JSON file where the data needs to be added to
    :param page_data: json, data that needs to be added
    :param item_id: str, ID of the product or Vendor
    """
    # Open the file and load the JSON dict
    with open(file_path) as json_file:
        data = json.load(json_file, strict=False)

    # Add the new data to the json file
    data[item_id] = page_data

    # Overwrite the old JSON dict with the new (more complete) JSON dict
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, default=myconverter)


def create_product_item_id_list(path_item_id):
    """
    Creates a JSON file which contains three types of lists (see returns) to keep track of all ID of the products.
    This function initializes this file.
    :param path_item_id: str, the path where the item_id is to be stored
    :return: item_idx: int, a counter that keeps track of the number of unique IDs given out
    :return: idx_finder: dict, {product_name+vendor_name : item_id}, a dict where the key is a combination of the
    product_name + the vendor_name, the value is the unique ID of the product. It can be so that different keys have the
    same values.
    :return: vendor_product_list: dict, {vendor_name : [product_id1, product_id2]}, In the dict the keys are names of
    the vendors. The list contains the product_ids.
    """

    item_idx = 0  # first_item_name will be market+product+'_1'
    idx_finder = {}  # {product_name+vendor_name : item_id}
    vendor_product_list = {}  # {vendor:[product1, product2]}
    item_id_list = {
        'item_idx': item_idx,
        'idx_finder': idx_finder,
        'vendor_product_list': vendor_product_list
    }
    # Create the json file
    with open(path_item_id, 'w') as outfile:
        json.dump(item_id_list, outfile)
    return item_idx, idx_finder, vendor_product_list


def open_item_id_list(path_item_id, page_type):
    """
    :param path_item_id:  str, the path where the item_id file is stored
    :param page_type:  str (vendor or product), the type of page
    :return: item_idx: int, a counter that keeps track of the number of unique IDs given out
    :return: idx_finder: dict, {product_name+vendor_name : item_id}, a dict where the key is a combination of the
    product_name + the vendor_name, the value is the unique ID of the product. It can be so that different keys have the
    same values.
    :return: vendor_product_list: dict, {vendor_name : [product_id1, product_id2]}, In the dict the keys are names of
    the vendors. The list contains the product_ids.
    :return: vendor_list: list, vendor_list containing the names of all the vendors
    """
    if page_type == 'product':
        with open(path_item_id) as json_file:
            data = json.load(json_file, strict=False)
        return data['item_idx'], data['idx_finder'], data['vendor_product_list']
    elif page_type == 'vendor':
        with open(path_item_id) as json_file:
            vendor_list = json.load(json_file, strict=False)
        return vendor_list


def update_item_id_list(product_idx, product_idx_finder, vendor_product_list, vendor_name, name, new_product_id):
    # add to list
    product_idx += 1
    product_idx_finder[vendor_name + '_' + name] = new_product_id
    if vendor_name not in vendor_product_list:
        vendor_product_list[vendor_name] = [new_product_id]
    else:
        vendor_product_list[vendor_name].append(new_product_id)
    return product_idx, product_idx_finder, vendor_product_list


def open_current_json(file_path):
    """
    Opens the current JSON file for the market and date of the page in consideration
    :param file_path: str, the path of the JSON file where the data needs to be added to
    :return: JSON, loaded from the file
    """
    with open(file_path) as json_file:
        return json.load(json_file, strict=False)


def store_json(imported_data, json_export_folder):
    """
    Loops through the data and checks the imported data against the stored stored JSON files.
    Determines the real IDs of the products. Provides new IDs and returns also OLD IDs.
    Exports nicely structured JSON files
    :param imported_data: list of data files created by the merge_files function.
    :param json_export_folder: the folder where the json where the json files are stored and will be stored:
    'json_export_folder/market/date/json_flles'
    :return: boolean, True if the process is finished
    """

    # check whether the JSON export folder exists
    if not os.path.isdir(json_export_folder):
        return 'The export folder of the json files does not exist, or your path is wrong'

    # loop over the files
    for page in imported_data:
        page_data = imported_data[page]

        # Retrieve market and date
        date, market, name, page_type = retrieve_market_and_date(page_data)
        date = datetime.datetime.fromtimestamp(date).strftime('%Y_%m_%d')  # datetime to str object

        # If product, then retrieve vendor name as well
        if page_type == 'product':
            vendor_name = page_data['page_data']['vendor']
            if vendor_name is None:
                vendor_name = 'NoVendorFound'
        else:
            vendor_name = None

        # Check folder of market and date, create if not exists, use function used by import
        create_market_folder(json_export_folder, market)
        new_path = create_date_folder(json_export_folder, market, date)

        # Item_id handler products, if folder does not exist yet: create
        path_product_item_folder = json_export_folder + '/item_id/'
        if not os.path.isdir(path_product_item_folder):
            os.mkdir(path_product_item_folder)

        # import the Item_id handler files
        path_product_item_id = json_export_folder + '/item_id/' + market + '_ProductID.txt'
        if os.path.isfile(path_product_item_id):
            # opens list
            product_idx, product_idx_finder, vendor_product_list = open_item_id_list(path_product_item_id, 'product')
        else:
            # creates and opens list
            product_idx, product_idx_finder, vendor_product_list = create_product_item_id_list(path_product_item_id)

        # Vendor_names handler products
        path_vendor_name_id = json_export_folder + '/item_id/' + market + '_VendorID.txt'
        if os.path.isfile(path_vendor_name_id):
            vendor_list = open_item_id_list(path_vendor_name_id, 'vendor')
        else:
            # create a new vendor_list
            vendor_list = []

        # check current file exists
        json_path = new_path + date + '_' + market + '_' + page_type + '.txt'
        if not os.path.isfile(json_path):
            current_json_exists = False
            current_json = None
        else:
            current_json_exists = True
            current_json = open_current_json(json_path)

        # Check previous file exists
        prev_json_exists = find_existing_json(json_export_folder, market, date, page_type)

        # If the page is a vendor; follow these steps
        if page_type == 'vendor':

            if not current_json_exists:
                # create a new export json file for the specific date
                export_new_json(json_path, page_data, name)

                # add vendor to list
                vendor_list.append(name)  # duplicates are removed later

            if current_json_exists:
                # check whether vendor name is already in file, if not; add
                if name not in current_json.keys():

                    add_to_existing_json(json_path, page_data, name)

                    # add name to vendor set
                    vendor_list.append(name)  # duplicates are removed later

                # The name of the vendor is already in the file, thus existed already
                else:
                    # File did exist already in the file
                    pass


        # If the page is a vendor; follow these steps
        if page_type == 'product':
            # print('________')
            # print(name)
            if prev_json_exists is False:

                if not current_json_exists:
                    # new id, because does not exist yet
                    new_product_id = market + '_' + page_type + '_' + str(product_idx + 1)

                    # create a new export json file
                    export_new_json(json_path, page_data, new_product_id)

                    # add to item_id
                    product_idx, product_idx_finder, vendor_product_list = update_item_id_list(product_idx,
                                                                                               product_idx_finder,
                                                                                               vendor_product_list,
                                                                                               vendor_name, name,
                                                                                               new_product_id)

                if current_json_exists:

                    # Check whether the product is already in the current json
                    existing = False  # boolean to check if the product is already in the current json
                    for idx in current_json:
                        if current_json[idx]['page_data']['vendor'] == vendor_name:
                            if current_json[idx]['page_data']['name'] == name:
                                existing = True  # The product already exists in the data

                    if not existing:
                        # new id, because does not exist yet
                        new_product_id = market + '_' + page_type + '_' + str(product_idx + 1)

                        # add to existing json
                        add_to_existing_json(json_path, page_data, new_product_id)

                        # add to list
                        product_idx, product_idx_finder, vendor_product_list = update_item_id_list(product_idx,
                                                                                                   product_idx_finder,
                                                                                                   vendor_product_list,
                                                                                                   vendor_name, name,
                                                                                                   new_product_id)
            # If previous JSON exists
            else:
                if not current_json_exists:
                    # initiate product_id
                    product_name = None
                    existing = False  # boolean to check if the product is already in the previous JSON

                    # first check if the name is the exact same
                    vendor_product = vendor_name + '_' + name  # unique identifier for the product_idx_finder
                    if vendor_product in product_idx_finder:
                        product_name = product_idx_finder[vendor_product]
                        existing = True  # the name exists already in the data

                    # If vendor_name is known, check which product_id to look into
                    elif vendor_name in vendor_product_list:
                        # Take five "older" reviews of this imported vendor / product
                        imported_reviews = retrieve_reviews(page_data)
                        # if there is no exact name, try to match on 5 old reviews, maybe the name of the
                        # product has changes
                        for product_id in vendor_product_list[vendor_name]:
                            # ? if product_id does not exist in previous
                            data_previous = open_current_json(prev_json_exists)
                            if product_id in data_previous:
                                prev_feedback = data_previous[product_id]['page_data']['feedback']
                                if imported_reviews is not None and prev_feedback is not None:
                                    feedback_counter = 0
                                    for feedback1 in imported_reviews:
                                        for feedback2 in prev_feedback:
                                            if feedback1['message'] == feedback2['message']:
                                                feedback_counter += 1
                                    if feedback_counter > 0:  # if more than 0 exist in both, the products are the same
                                        existing = True  # the product exists already in the data
                                        product_name = product_id

                    # If there is product found that is the same, create new id
                    if product_name is None:
                        # new id, because does not exist yet
                        product_name = market + '_' + page_type + '_' + str(product_idx + 1)

                    # create a new export json file
                    export_new_json(json_path, page_data, product_name)

                    # add to list
                    if not existing:
                        product_idx, product_idx_finder, vendor_product_list = update_item_id_list(product_idx,
                                                                                                   product_idx_finder,
                                                                                                   vendor_product_list,
                                                                                                   vendor_name, name,
                                                                                                   product_name)

                if current_json_exists:
                    # initiate product_id
                    product_name = None
                    existing = False  # boolean to check if the product is already in the previous or current JSON

                    # check if product is already in current json file
                    vendor_product = vendor_name + '_' + name  # unique identifier for the product_idx_finder
                    if vendor_product in product_idx_finder:
                        product_name = product_idx_finder[vendor_product]
                        if product_name in current_json:
                            pass
                        else:
                            # same name, not yet in current thus add
                            # add to existing json
                            add_to_existing_json(json_path, page_data, product_name)

                    # Check whether the product name has changed
                    elif vendor_name in vendor_product_list:
                        # Take five "older" reviews of this imported vendor / product
                        imported_reviews = retrieve_reviews(page_data)

                        # if there is no exact name, try to match on 5 old reviews
                        for product_id in vendor_product_list[vendor_name]:
                            prev_feedback = open_current_json(prev_json_exists)  # [product_id]['page_data']['feedback']
                            if product_id in prev_feedback:
                                prev_feedback = prev_feedback[product_id]['page_data']['feedback']
                                if imported_reviews is not None and prev_feedback is not None:
                                    feedback_counter = 0
                                    for feedback1 in imported_reviews:
                                        for feedback2 in prev_feedback:
                                            if feedback1['message'] == feedback2['message']:
                                                feedback_counter += 1
                                    if feedback_counter > 0:
                                        product_name = product_id
                                        existing = True
                                        continue  # will break the loop and continues

                        # new id, because does not exist yet
                        if product_name is None:
                            product_name = market + '_' + page_type + '_' + str(product_idx + 1)

                        # create a new export json file
                        add_to_existing_json(json_path, page_data, product_name)
                        # add to list
                        if not existing:
                            product_idx, product_idx_finder, vendor_product_list = \
                                update_item_id_list(product_idx, product_idx_finder, vendor_product_list, vendor_name,
                                                    name, product_name)

                    # When the vendor is completely new and was never recorded before
                    else:
                        product_name = market + '_' + page_type + '_' + str(product_idx + 1)
                        add_to_existing_json(json_path, page_data, product_name)
                        product_idx, product_idx_finder, vendor_product_list = \
                            update_item_id_list(product_idx, product_idx_finder, vendor_product_list, vendor_name,
                                                name, product_name)

        # Export vendor_list
        vendor_list = list(set(vendor_list))
        with open(path_vendor_name_id, 'w') as outfile:
            json.dump(vendor_list, outfile)

        # Export product_item dict
        product_item_output = {
            'item_idx': product_idx,
            'idx_finder': product_idx_finder,
            'vendor_product_list': vendor_product_list
        }
        with open(path_product_item_id, 'w') as outfile:
            json.dump(product_item_output, outfile)

    return True
