"""
html_file import module
This module is part of ANITA

This module contains function for the import and sorting of raw HTML files and there accompanying folders.
"""

import os
import datetime
import zipfile
import shutil
from .Scraper import determine_market, open_folder, import_market_modules, get_soup


def check_date_folder(file_paths):
    """ Input is a list of file_paths
    For the given files a data is returned if the data is in the tree structure in the right format
    The right format for a data in the tree structure is yyyy_mm_dd
    If no right format can be found a list of folders with the wrong structure is raised
    The function returns a dictionary: page_date_dict[file_path] = (date, date_in_name)
    where:
    Date is the date in datetime format
    Date_in_name is a boolean (True/False) that is True when "yyyy_mm_dd" is already in the file name """

    # initiate
    page_date_dict = {}  # dict with values (date, date_in_name)
    problem_folder = set()  # list with folders that do not contain a data and can be a problem

    # loop through all the files to add the date per file
    for file_path in file_paths:
        page_tree = file_path.split('/')
        path_length = len(page_tree)
        path_idx = path_length - 1  # start at counting 0 instead of 1

        # initiate
        date = None
        date_in_name = False
        date_name = None

        # Loop through the page_tree to find the date in the folder name
        # The date of the folder closest to the file in the structure will be used as the date of the file
        # Thus: in this tree (2019_01_01/2020_01_01/file1.html) file1 will have 2020_01_01 as date
        while path_idx >= 0:

            # try to extract the date
            try:
                date = datetime.datetime.strptime(page_tree[path_idx][0:10], '%Y_%m_%d').date()

                # check whether the date is already in the file name
                if path_idx == path_length - 1:  # (path_length - 1) is the file name
                    date_in_name = True
                    date_name = date  # in this case look further, because the date must be in folder name
                    date = None
                else:
                    break


            # if the date cannot be found in that part of the page_tree
            except ValueError:
                # add the the path to the problem folder set of this was the last part of the loop
                if path_idx == 0:
                    problem_folder.add('/'.join(file_path.split('/')[:-1]))

            path_idx -= 1

        # If for some weird case the date in the name is different form the folder. Follow the folder date.
        # The new date (folder date) will be added before the file name with the wrong date

        if (date_in_name is True) and (date_name != date):
            date_in_name = False
        page_date_dict[file_path] = (date, date_in_name)

    # if no problems were found, return the page_date_dict
    if len(problem_folder) == 0:
        return page_date_dict

    # if problems were found, print the problem and the problem list and return False
    else:
        print('There is a problem in the formatting of the date in the folder. Make sure to include the date ('
              'yyyy_mm_dd) in the beginning of the folder name')
        print('This applies to the following folders:')
        for file_path in problem_folder:
            print(file_path)

        return False


def create_market_folder(main_target_path, market):
    """Create a market folder if it not exists in the main_target_path"""
    path = main_target_path + market + '/'
    if not os.path.isdir(path):
        os.mkdir(path)


def create_date_folder(main_target_path, market, date):
    """Creates a date folder in the market folder if it not exists in the main_target_path/market"""
    path = main_target_path + market + '/' + date + '/'
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


def change_file_name(file_path, date, market):
    """Change the name current files to yyyy_mm_dd_market_filename in the path"""

    if (file_path.split('/')[-2] != date) and (file_path.split('/')[-2] != market):
        file_name = file_path.split('/')[-2] + '_' + file_path.split('/')[-1]
    else:
        file_name = file_path.split('/')[-1]

    new_file_name = date + '_' + file_name
    return new_file_name


def move_file_and_folder(current_path, new_path, date, market, add_date=False):
    """The files will be moved to the correct place in the folder
    current_path is path to the current existing file
    new_path is the path where to move to
    date is the date that belongs to the specific file
    add_date is True when the date needs to be added to the filename"""

    # define the name and paths of the file and folder

    if add_date:
        file_name = change_file_name(current_path, date, market)
        folder_name = '.'.join(file_name.split('.')[:-1]) + '_files'

    else:
        if (current_path.split('/')[-2] != date) and (current_path.split('/')[-2] != market):
            file_name = current_path.split('/')[-2] + '_' + current_path.split('/')[-1]
        else:
            file_name = current_path.split('/')[-1]
        folder_name = '.'.join(file_name.split('.')[:-1]) + '_files'

    current_path_file = current_path
    current_path_folder = '.'.join(current_path.split('.')[:-1]) + '_files'
    new_path_file = new_path + file_name
    new_path_folder = new_path + folder_name

    # initialize
    moved_file_path = None
    # move the files
    if os.path.isfile(current_path_file):
        if os.path.isfile(new_path_file):
            print('The file you try to import, already exists in the database')
            print(current_path_file)
            print('The current folder in the database will be kept, you can ignore this message')
            print(' ')
        if not os.path.isfile(new_path_file):
            os.rename(current_path_file, new_path_file)
            moved_file_path = new_path_file
    # move the accompanying folder and files
    if os.path.isdir(current_path_folder):
        if os.path.isdir(new_path_folder):
            print('The folder you try to move, already exists')
            print(current_path_folder)
            print('The current folder in the database will be kept, you can ignore this message')
            print(' ')
        if not os.path.isdir(new_path_folder):
            os.rename(current_path_folder, new_path_folder)

    # return the file that is moved
    return moved_file_path


def open_zip(zipfile_path):
    """Extracts the zipfile in the same folder and creates a folder with the same name containing the files
    Removes the ZIP file afterwards"""
    new_path = zipfile_path[:-4]

    # create the folder to output
    if not os.path.isdir(new_path):
        os.mkdir(new_path)

    # find all the files to output in that folder and extract
    with zipfile.ZipFile(zipfile_path, "r") as zip_ref:
        for file_tree in sorted(zip_ref.namelist()):
            # when on a mac, do not copy these files
            if not file_tree.startswith('__MACOSX'):
                zip_ref.extract(file_tree, new_path)

    # remove Zip file afterwards
    os.remove(zipfile_path)

    # return the new path to import these files
    return new_path


def import_files(import_path, main_target_path, delete_files=False):
    """Main import function
    Parameters:
        import_path : the path to where the files currently are
        main_target_path : the path where the market files are structurally stored
        delete_files: when true the folder in the path will be deleted"""

    # check whether folder or zip exists
    if not os.path.isdir(import_path) and not zipfile.is_zipfile(import_path):
        return 'The folder of file does not exist, or your path is wrong'

    # If path is to a string, extract zip and continue with folder
    if zipfile.is_zipfile(import_path):
        import_path = open_zip(import_path)

    # open the folder and create a list of the paths of the files
    file_paths = open_folder(import_path)
    # Check the date of the folder / file, and get a dict with the date per file
    files = check_date_folder(file_paths)

    # import all different market modules
    market_modules = import_market_modules()


    if files is not False:
        # keep a list of moved files, which need yet to be processed
        moved_files = []

        #keep track of amount
        len_total_files = len(files)
        counter = 1

        for file_path in files.keys():
            # get soup
            try:
                soup_file = get_soup(file_path)
            except UnicodeDecodeError:
                print('UnicodeDecodeError')
                print(file_path)
                continue
            except:
                print('This should not be printed, this a problem')
                print(file_path)

                continue

            # determine market
            market = determine_market(soup_file)

            if (market is not False) and (market is not None):

                # determine page_type
                page_type = market_modules[market].pagetype(soup_file)

                # We are only interested in vendor and product pages
                if (page_type == 'vendor') or (page_type == 'product'):

                    # create date and market folder if not existing
                    date = files[file_path][0].strftime('%Y_%m_%d')
                    create_market_folder(main_target_path, market)
                    new_path = create_date_folder(main_target_path, market, date)

                    # move the folder and file
                    moved_file = move_file_and_folder(file_path, new_path, date, market, add_date=not files[file_path][1])
                    if moved_file is not None:
                        moved_files.append(moved_file)

            counter += 1
            if counter % (len_total_files / 100) == 0:
                print(counter/len_total_files)



        # end with removing the folder
        if delete_files:
            shutil.rmtree(import_path)
        # return a list of the moved files
        return moved_files
    # return error if the something went wrong in finding the paths
    else:
        return 'see error above'


class Test:
    def test(self, value):
        print(value)
