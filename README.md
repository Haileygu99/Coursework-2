# Coursework-2 

## Overview

The datasets in this folder contains information decribing geographical, educational, demographic and lifestyle variables for a set of people who all currently live in the United Kingdom. There are two forms of the dataset. The dataset that is to be shared with the Government is called 'Government Dataset', and the other dataset that is to be shared with researchers is called the 'Imperial Researchers Dataset'.

## Instructions for decrypt the Imperial researchers Dataset csv file.

```
# using the key
fernet = Fernet(key)
```
```
# opening the encrypted file
with open ('Imperial Researchers Dataset.csv', 'rb') as enc_Imperial_Researchers_Dataset_file:
  encrypted = enc_Imperial_Researchers_Dataset_file.read()
```
```
# decrypting the file
decrypted = fernet.decrypt(encrypted)
```
```
# opening the file in write mode and 
# writing the decrypted data
with open('Imperial Researchers Dataset.csv', 'wb') as dec_Imperial_Researchers_Dataset_file:
  dec_Imperial_Researchers_Dataset_file.write(decrypted)
```


## Instructions for decrypt the Government Dataset csv file.

```
# using the key
fernet = Fernet(key)
```
```
# opening the encrypted file
with open ('Government Dataset.csv', 'rb') as enc_Government_Dataset_file:
  encrypted = enc_Government_Dataset_file.read()
```
```
# decrypting the file
decrypted = fernet.decrypt(encrypted)
```
```
# opening the file in write mode and 
# writing the decrypted data
with open('Government Dataset.csv', 'wb') as dec_Government_Dataset_file:
  dec_Government_Dataset_file.write(decrypted)
```
