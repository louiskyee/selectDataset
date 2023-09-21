from tqdm import tqdm
import numpy as np
import argparse
import random
import pickle
import glob
import tlsh
import time
import os

DEFAULT_INPUT_PATH = "./dataset/"
DEFAULT_TIMES_LESS = 5

class selectDataset(object):
    def __init__(self):
        self.datasetPath = DEFAULT_INPUT_PATH
        self.timesLess = DEFAULT_TIMES_LESS
        self.number_of_choose_files = 0
        self.hash_dict = {}
        self.matrix = np.full((0, 0), -1.0, dtype=float)
        self.fileNames = []
        self.choosed_files = []
        self.min_values = np.full(0, np.inf)
        self.nextIdx = -1
        self.maxValue = -np.inf
        self.file_list = []
        self.hash_list = []
        self.weight_list = []        

    def run(self):
        self.parameter_parser()
        self.get_file_list()
        self.get_choosed_files()
        self.write_hash_dict()
        self.write_choosed_files_to_txt()

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
        args = parser.parse_args()
        
        # Check if args.input_folder and args.times_less are defined, if not, use defaults
        self.datasetPath = args.input_folder if hasattr(args, 'input_folder') else DEFAULT_INPUT_PATH
        self.timesLess = int(args.times_less) if hasattr(args, 'times_less') else DEFAULT_TIMES_LESS

    def get_file_list(self):
        self.file_list = glob.glob(os.path.join(self.datasetPath, "*"))

    def write_hash_dict(self):
        with open("./hash_dict.pickle", "wb") as f:
            pickle.dump(self.hash_dict, f)

    def read_hash_dict(self):
        with open("./hash_dict.pickle", "rb") as f:
            self.hash_dict = pickle.load(f)

    def write_choosed_files_to_txt(self):
        with open("./choosed_files.txt", "w") as f:
            for file in self.choosed_files:
                f.write(f"{file}\n")

    def __get_next_file(self, rowIdx):
        # Initialize the maximum value and the next index
        nextIdx = -1
        maxValue = -np.inf

        # Iterate over the column indices of the matrix
        for colIdx, value in enumerate(self.matrix[rowIdx]):
            # Check if this column needs to be considered
            if value >= 0.0 and self.fileNames[colIdx] not in self.choosed_files:
                # Find the minimum value in this
                self.min_values[colIdx] = min(self.min_values[colIdx], value)
                if maxValue < self.min_values[colIdx]:
                    maxValue = self.min_values[colIdx]
                    nextIdx = colIdx
        self.min_values[nextIdx] = -1

        return nextIdx

    def __calculate_weight(self):
        curFile:str = random.sample(self.fileNames, 1)[0]  # random select first file
        self.choosed_files = [curFile]
        self.min_values[self.fileNames.index(curFile)] = -1
        while len(self.choosed_files) < self.number_of_choose_files:
            rowIdx = self.fileNames.index(curFile)
            hashValue1 = self.hash_dict[curFile]
            for fileName in self.fileNames:
                if fileName in self.choosed_files or fileName == curFile:
                    continue

                hashValue2 = self.hash_dict[fileName]
                colIdx = self.fileNames.index(fileName)

                # Check if the weight has been calculated before
                if self.matrix[rowIdx, colIdx] == -1.0:
                    weight = tlsh.diff(hashValue1, hashValue2)
                    self.matrix[rowIdx, colIdx] = weight
                    self.matrix[colIdx, rowIdx] = weight
            nextIdx = self.__get_next_file(rowIdx)
            curFile = self.fileNames[nextIdx]
            self.choosed_files.append(curFile)

    def get_choosed_files(self):
        start_time = time.time()
        for filePath in tqdm(self.file_list, desc=f"Calculating tlsh hash"):
            hashValue = tlsh.hash(open(filePath, 'rb').read())
            fileName = os.path.basename(filePath)
            self.hash_dict[fileName] = hashValue

        self.number_of_choose_files = len(self.hash_dict) // self.timesLess
        print(f"number of choosed files = {self.number_of_choose_files}")
        n = len(self.hash_dict)
        self.fileNames:list = list(self.hash_dict.keys())
        self.matrix = np.full((n, n), -1.0, dtype=float)
        self.min_values = np.full(n, np.inf)
        self.__calculate_weight()

        end_time = time.time()

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"tlsh elapsed time: {elapsed_time:.2f}")

if __name__ == "__main__":
    selectDataset().run()