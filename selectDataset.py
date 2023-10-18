from tqdm import tqdm
import numpy as np
import argparse
import random
import pickle
import tlsh
import time
import os

DEFAULT_INPUT_PATH = "./dataset/"
DEFAULT_TIMES_LESS = 5
DEFAULT_PICKLE_FILE_PATH = "./hash_dict.pickle"

class selectDataset(object):
    def __init__(self):
        '''
        Initialize default values for various parameters
        '''
        self.datasetPath = DEFAULT_INPUT_PATH  # Default input dataset folder path
        self.timesLess = DEFAULT_TIMES_LESS  # Default fraction of the original data set
        self.pickle_file_path = DEFAULT_PICKLE_FILE_PATH  # Default path for the pickle file
        self.number_of_choose_files = 0  # Number of files to choose based on criteria
        self.hash_dict = {}  # Dictionary to store hash values for files
        self.fileNames = []  # List to store file names
        self.chosen_files = []  # List to store selected files
        self.min_values = np.full(0, np.inf)  # Array to store minimum values for file comparisons and track available files (initially all available), -1 means unavailable
        self.file_list = []  # List to store file paths
       
    def run(self):
        self.parameter_parser()
        self.get_all_files_in_directory()
        self.get_chosen_files()
        self.write_chosen_files_to_txt()

    def parameter_parser(self):
        '''
        A method for parsing command line parameters
        using `python argparse`.
        '''
        parser = argparse.ArgumentParser(description="Parse command line parameters.")
    
        parser.add_argument("--input-folder", "-i",
                            dest="input_folder",
                            nargs="?",
                            default=DEFAULT_INPUT_PATH,
                            help="Input dataset folder."
                            )
        parser.add_argument("--timesLess", "-t",
                            dest="times_less",
                            nargs="?",
                            default=DEFAULT_TIMES_LESS,
                            help="Take a fraction of the original data set."
                            )
        parser.add_argument("--pickle-file", "-p",
                            dest="pickle_file",
                            nargs="?",
                            default=None,
                            help="Full path to the pickle file containing hash_dict data."
                            )
        args = parser.parse_args()
    
        # Check if args.input_folder and args.times_less are defined, if not, use defaults
        self.datasetPath = args.input_folder
        self.timesLess = int(args.times_less)
        
        # Load hash_dict from pickle file if provided
        if args.pickle_file:
            self.pickle_file_path = args.pickle_file
            self.read_hash_dict()            

    def get_all_files_in_directory(self):
        '''
        Get a list of all files in the folder and its subfolders
        '''
        for root, dirs, files in os.walk(self.datasetPath):
            for file in files:
                file_path = os.path.join(root, file)
                self.file_list.append(file_path)

    def write_hash_dict(self):
        '''
        Write the hash_dict to a pickle file
        '''
        with open(self.pickle_file_path, "wb") as f:
            pickle.dump(self.hash_dict, f)

    def read_hash_dict(self):
        if os.path.exists(self.pickle_file_path):
            # Read the hash_dict from the specified pickle file if it exists
            with open(self.pickle_file_path, 'rb') as pickle_file:
                self.hash_dict = pickle.load(pickle_file)
                print(f"Loaded hash_dict from {self.pickle_file_path}")
        else:
            # Initialize an empty hash_dict if the pickle file doesn't exist
            self.hash_dict = {}
            print(f"Warning: Pickle file '{self.pickle_file_path}' not found. Using an empty hash_dict.")

    def write_chosen_files_to_txt(self):
        '''
        Write the list of chosen files to a text file
        '''
        with open("./chosen_files.txt", "w") as f:
            for file in self.chosen_files:
                f.write(f"{file}\n")
        self.__delete_backup_file()

    def __delete_backup_file(self):
        '''
        Delete the backup file if it exists
        '''
        if os.path.exists("./chosen_files_backup.txt"):
            os.remove("./chosen_files_backup.txt")

    def __calculate_weight(self):
        self.__delete_backup_file()

        # Add the selected file to the list of chosen files
        with open("./chosen_files_backup.txt", "a") as backup_f:
            # Randomly select the first file
            curFileIdx = random.randint(0, len(self.fileNames) - 1)
            curFile = self.fileNames[curFileIdx]
            self.chosen_files.append(curFile)

            # Initialize the minimum value for the selected file to -1
            self.min_values[curFileIdx] = -1

            backup_f.write(f"{curFile}\n")

            while len(self.chosen_files) < self.number_of_choose_files:
                # Calculate the hash value of the current file
                hashValue1 = self.hash_dict[curFile]
                maxValue = -np.inf
                nextIdx = -1
        
                # Iterate through the file names and indices
                for idx, fileName in enumerate(self.fileNames):
                    if self.min_values[idx] != -1:
                        # Calculate the hash value of the current comparison file
                        hashValue2 = self.hash_dict[fileName]
                        # Update the minimum value for the comparison file
                        if self.min_values[idx] == np.inf:
                            self.min_values[idx] = min(self.min_values[idx], tlsh.diff(hashValue1, hashValue2))
                        # Find the maximum value among the available comparison files
                        maxValue, nextIdx = max((maxValue, nextIdx), (self.min_values[idx], idx))
        
                # Mark the selected comparison file as unavailable
                self.min_values[nextIdx] = -1
                curFile = self.fileNames[nextIdx]

                # Add the selected file to the list of chosen files
                self.chosen_files.append(curFile)

                # backup the selected file
                backup_f.write(f"{curFile}\n")

    def get_chosen_files(self):
        # Measure the start time
        start_time = time.time()
    
        # Calculate TLSH hash values for each file in the list if hash_dict is empty
        if not self.hash_dict:
            for filePath in tqdm(self.file_list, desc="Calculating tlsh hash"):
                hashValue = tlsh.hash(open(filePath, 'rb').read())
                fileName = os.path.basename(filePath)
                self.hash_dict[fileName] = hashValue
    
            # Write the hash dictionary to a file
            self.write_hash_dict()
    
        # Calculate the number of files to choose based on criteria
        self.number_of_choose_files = len(self.hash_dict) // self.timesLess
        print(f"number of chosen files = {self.number_of_choose_files}")
    
        n = len(self.hash_dict)
    
        # Get the list of file names from the hash dictionary
        self.fileNames: list = list(self.hash_dict.keys())
    
        # Initialize arrays to track available files and minimum values
        self.min_values = np.full(n, np.inf)
    
        # Calculate file weights for selection
        self.__calculate_weight()
    
        # Measure the end time
        end_time = time.time()
    
        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"tlsh elapsed time: {elapsed_time:.2f}")

if __name__ == "__main__":
    selectDataset().run()