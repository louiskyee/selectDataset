# selectDataset

## Introduction
The primary function is to allow users to select the most dispersed samples from an existing dataset. The core technology employed is Trend Micro Locality Sensitive Hash (available on [GitHub](https://github.com/trendmicro/tlsh.git)). The time complexity is O(m*n), where n represents the size of the dataset, and m represents the number of data points selected.

## Prerequisites
* python >= 3.10
* package
  ```cmd=
  pip3 install tqdm
  pip3 install numpy
  pip3 install py-tlsh
  ```

## Useage
```python=
python3 selectDataset.py -i <datasetFolder> -t <timesLess> -p <pickle_file>
```
### parameter
* `-i`: (`--input-folder`)
  * datasetFolder: The folder path that stores binary ELF files.
* `-t`: (`--timesLess`)
  * timesLess: Specify the fraction of the dataset to obtain. If you input 5, it means to take one-fifth (1/5) of the dataset.
* `-p`: (`--pickle-file`)
  * pickle_file: Specify the full hash_dict.pickle file path to be read. The hach_dict.pickle file containing hash_dict data.

### Output
* `choosed_files.txt`: This file contains a list of selected files.
* `chosen_files_backup.txt`: Create a backup of the currently selected files. If `chosen_files_backup.txt` exists, but `choosed_files.txt` does not, it means that the file was not retrieved completely.
* `hash_dict.pickle`: This file utilizes a dictionary structure to store the TLSh hash values of all files.
  * Format: `<fileName>: <tlshValue>`

### Example
```python=
python3 selectDataset.py -i ./dataset/ -t 5 -p ./hash_dict.pickle
```
