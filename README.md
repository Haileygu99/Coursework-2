# Coursework-2 


Instructions for decrypt the data file.

```
# using the key
fernet = Fernet(key)
```
```
# opening the encrypted file
with open ('new_cust.csv', 'rb') as enc_new_cust_file:
  encrypted = enc_cust_file.read()
```
```
# decrypting the file
decrypted = fernet.decrypt(encrypted)
```
```
# opening the file in write mode and 
# writing the decrypted data
with open('new_cust.csv', 'wb') as dec_new_cust_file:
  dec_new_cust_file.write(decrypted)
```
