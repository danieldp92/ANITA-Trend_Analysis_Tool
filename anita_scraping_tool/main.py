import os
import sys
import anita.ImportFile as importfile
import anita.Scraper as scraper
import anita.Merge as merge


if __name__ == "__main__":
    # Input parameters

    # dump_path
    dump_path = input("Insert zip or folder path of dump: ")

    if not os.path.exists(dump_path):
        print("Invalid path!!!")
        # More controls could be useful
        sys.exit(0)

    os.system('cls' if os.name == 'nt' else 'clear')

    # Sorted_files_path
    # created a suggested path to store the files
    suggested_export_folder = '/'.join(dump_path.split('/')[:-2]) + '/'
    print(f'Suggested export folder where to store the sorted/filtered files: {suggested_export_folder}')
    sorted_files_path = input("Enter folder path where to store the sorted/filtered files if you want to deviate, to accept suggested leave empty: ")

    if sorted_files_path == '':
        sorted_files_path = suggested_export_folder

    if not os.path.isdir(sorted_files_path):
        print("The output path for sorted and filtered files must be a directory")
        sys.exit(0)

    os.system('cls' if os.name == 'nt' else 'clear')

    # output_json_path
    output_json_path = input("Insert output path for json files: ")

    if not os.path.isdir(output_json_path):
        print("The output path must be a directory")
        sys.exit(0)

    os.system('cls' if os.name == 'nt' else 'clear')

    # Summary & start
    print('SUMMARY')
    print(f'The following folder will be exported: {dump_path}')
    print(f'The filtered and sorted files will be stored in: {sorted_files_path}')
    print(f'The JSON files will be sort in: {output_json_path}')
    print('Is everything correct?')
    start_processing = input("'Y' for starting the process: ")

    if start_processing.lower() != 'y':
        sys.exit(0)

    else:
        print('Starting exporting the files...')

    # PROCESSING
    print('Data filtering and moving started')
    print('Depending on the size of the folder, this can take a lot of time')
    importfile.import_files(dump_path, sorted_files_path, delete_files=True)
    print(f'Data moving complete, filtered data can be found in: {sorted_files_path}')

    print('Scraping data from files started')
    print('Depending on the size of the folder, this can take a lot of time')
    data = scraper.json(sorted_files_path)
    print('Scraping data from files completed')

    print('Merging duplicate vendors and products has started')
    merged_data = merge.merge_items(data)
    print('Merging duplicate vendors and products is completed')

    # SAVE JSON INTO THE OUTPUT FOLDER
    print('Exporting the data into JSON has started')
    merge.store_json(merged_data, output_json_path)

    os.system('cls' if os.name == 'nt' else 'clear')
    print('The process has finished!')
    print(f'Files from the following folder are exported: {dump_path}')
    print(f'The filtered and sorted files will are stored in: {sorted_files_path}')
    print(f'The JSON files can be found here: {output_json_path}')

    sys.exit(0)

