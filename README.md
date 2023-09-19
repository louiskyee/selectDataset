# selectDataset
Select the most dispersed results on the existing data set

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
python3 selectDataset.py -i <datasetFolder> -t <timesLess>
```
### parameter
* -i: input_folder
  * datasetFolder:  The folder path that stores binary ELF files.
* -t: times_less
  * timesLess: Specify the fraction of the dataset to obtain. If you input 5, it means to take one-fifth (1/5) of the dataset.

### Output
* `choosed_files.txt`: This file contains a list of selected files.
* `hash_dict.pickle`: This file utilizes a dictionary structure to store the TLSh hash values of all files.
  * Format: `<fileName>: <tlshValue>`

### Example
```python=
python3 selectDataset.py -i ./dataset/ -t 5
```
