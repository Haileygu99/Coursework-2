# Packages loading

import pandas as pd
import datetime
import matplotlib.pyplot as plt
from datetime import date
import hashlib
import random, string
from cryptography.fernet import Fernet
import pycountry_convert as pc  #pip install pycountry-convert

# Import data and target
df = pd.read_csv('customer_information.csv') #Using relative path

#Converting columns "weight" and "height" into numeric.
df["weight"] = pd.to_numeric(df["weight"])
df["height"] = pd.to_numeric(df["height"])
df['heightsquared']=df['height']**2

#Converting to BMI
df['bmi']=df['weight']/df['heightsquared']
df['bmi']=df['bmi'].apply(lambda x:round(x,2))

#Deleting the intermediate column 'heightsquared'
del df['heightsquared']

#Generate a function to convert birthdate to age group
#Intermediate year of birth column for calculating age
birthdate=pd.to_datetime(df.birthdate)
df['birth_year'] = pd.DatetimeIndex(birthdate).year

#Age calculation
def from_birthdate_to_age(birth_date):
    now=pd.Timestamp('now')
    now_year,now_month,now_day = now.year, now.month, now.day
    birth_date = pd.to_datetime(birth_date)
    birth_year, birth_month, birth_day = birth_date.year, birth_date.month, birth_date.day
    age = now_year - birth_year
    if now_month >= birth_month:
        if now_day >= birth_day:
            age = now_year - birth_year + 1
    return (age)

df['age'] = df['birthdate'].apply(from_birthdate_to_age)

#Banding age to groups
bins_age = [18,27,37,47,57,67]
labels_age= ['18-27','28-37','38-47','48-57','58-67']
df['age_groups'] = pd.cut(df.age, bins = bins_age, labels = labels_age)

# Banding 'BMI' to groups
##0-18.5 as underweight, 18.5-24.9 as healthy,24.9 and over as overweight

bins_bmi = [0,18.5,24.9,50]
label_bmi = ['Underweight','Healthy','Overweight']
df['level of bmi'] = pd.cut(df.bmi, bins = bins_bmi, labels = label_bmi, right = False)

# Country_of_birth mapping to continents
replace_dict={'Korea':'South Korea','Palestinian Territory':'Jordan','Saint Barthelemy':'Dominican Republic','Saint Helena': 'South Africa',
'Reunion': 'Mauritius','Svalbard and Jan Mayen':'Greenland','United States Minor Outlying Islands':'United States',
'Antarctica (the territory South of 60 deg S)': 'Heard Island and McDonald Islands','Western Sahara':'Morocco','Svalbard & Jan Mayen Islands':'Heard Island and McDonald Islands',
'Libyan Arab Jamahiriya':'Libya','Pitcairn Islands':'Fiji','Slovakia (Slovak Republic)':'Slovakia','Bouvet Island (Bouvetoya)':'Heard Island and McDonald Islands',
'Holy See (Vatican City State)':'Italy','Timor-Leste':'Indonesia',"Cote d'Ivoire":'Ghana','British Indian Ocean Territory (Chagos Archipelago)':'India',
"Netherlands Antilles":"Netherlands"}
df['country_of_birth'].replace(replace_dict,inplace=True)

# Group original countries to continent by applying a function to dataframe
def country_to_continent(country_of_birth):
    country_alpha2 = pc.country_name_to_country_alpha2(country_of_birth)
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name
df['continent_of_birth'] = df['country_of_birth'].apply(country_to_continent)

# Group some continents according to geographic / cultural reasons to improve K-anonymity
df['continent_of_birth'].replace({'North America':'America','South America':'America','Antarctica':'Europe'},inplace=True)

# Banding of education
df['education_level'].replace({'secondary':'pre-uni',
'primary': 'pre-uni',
'bachelor': 'bachelor',
'other': 'bachelor',
'masters': 'post-grad',
'phD':'post-grad'},inplace=True)

#SHA 
#Salt generator
def randomword(length):
   letters = string.ascii_lowercase #generates lowercase letters
   return ''.join(random.choice(letters) for i in range(length)) #generates salt from letters

df['NI_enc']=df['national_insurance_number'].str.encode('utf-8') #utf encoding needed for sha function

key='h8jij4f3'.encode('utf-8') #encoding key

#Hash function
hashes=[]
salt=[]
for i in range(len(df['NI_enc'])):
    salt.append(randomword(10).encode('utf-8'))
    hashes.append(hashlib.sha1(key+salt[i]+df['NI_enc'][i]).hexdigest()) #hash function applied 

df['hash']=hashes 
hash_cols=['given_name','surname','phone_number','national_insurance_number','blood_group',
'postcode','birthdate','age','bank_account_number','birth_year','avg_n_drinks_per_week',
'avg_n_cigret_per_week','bmi','country_of_birth','height','weight']

#Lookup table generation
secure_df=df[hash_cols]
secure_df['hash']=df['hash']
secure_df['salt']=salt
secure_df.drop(columns=['age','birth_year','bmi','bank_account_number'],inplace=True)
secure_df.set_index('hash',inplace=True)#This is the sensitive dataset that is not shared
new_cust=df.drop(columns=hash_cols)
new_cust=new_cust.drop(columns='NI_enc')
new_cust.set_index('hash',inplace=True)

# K-anonyminity for Imperial dataset
quasi_identifiers_imp=['age_groups','level of bmi','gender']
k_df_imp=new_cust.groupby(quasi_identifiers_imp,observed=True).size().reset_index(name='Count').sort_values(by='Count')
print(f'The Imperial K-anonyminity is: {min(k_df_imp["Count"])}')

# K-anonyminity for government dataset
quasi_identifiers_gov=['level of bmi','continent_of_birth','education_level']
k_df_gov=new_cust.groupby(quasi_identifiers_gov,observed=True).size().reset_index(name='Count').sort_values(by='Count')
print(f'The Government K-anonyminity is: {min(k_df_gov["Count"])}')

# convert the dataframe into csv for imperial researchers and government separately
imp_df=new_cust[['gender','age_groups','n_countries_visited','cc_status','level of bmi','level of drinking_status','smoking_status']]
gov_df=new_cust[['continent_of_birth','education_level','cc_status','level of bmi','level of drinking_status','smoking_status']]
imp_df.to_csv('Imperial Researchers Dataset.csv')
gov_df.to_csv('Government Dataset.csv')
secure_df.to_csv('Secure Dataset.csv')

# key generation 
key = Fernet.generate_key()

# string the key in a file
with open ('filekey.key', 'wb') as filekey:
    filekey.write(key)

# opening the key 
with open ('filekey.key', 'rb') as filekey:
    key = filekey.read()

# using the generated key 
fernet = Fernet (key)

# opening the original file to encrypt
with open('Imperial Researchers Dataset.csv', 'rb') as Imperial_Researchers_Dataset_file:
    original = Imperial_Researchers_Dataset_file.read()

# encrypting the file
encrypted = fernet.encrypt(original)

# opening the file in write mode and 
# writing the encrypted data
with open ('Imperial Researchers Dataset.csv', 'wb') as encrypted_Imperial_Researchers_Dataset_file:
    encrypted_Imperial_Researchers_Dataset_file.write(encrypted)

# opening the key 
with open ('filekey.key', 'rb') as filekey:
    key = filekey.read()

# using the generated key 
fernet = Fernet (key)

# opening the original file to encrypt
with open('Government Dataset.csv', 'rb') as Government_Dataset_file:
    original = Government_Dataset_file.read()

# encrypting the file
encrypted = fernet.encrypt(original)

# opening the file in write mode and 
# writing the encrypted data
with open ('Government Dataset.csv', 'wb') as encrypted_Government_Dataset_file:
    encrypted_Government_Dataset_file.write(encrypted)

# using the key
fernet = Fernet(key)


# opening the encrypted file
with open ('Imperial Researchers Dataset.csv', 'rb') as enc_Imperial_Researchers_Dataset_file:
  encrypted = enc_Imperial_Researchers_Dataset_file.read()


# decrypting the file
decrypted = fernet.decrypt(encrypted)


# opening the file in write mode and 
# writing the decrypted data
with open('Imperial Researchers Dataset.csv', 'wb') as dec_Imperial_Researchers_Dataset_file:
  dec_Imperial_Researchers_Dataset_file.write(decrypted)

# using the key
fernet = Fernet(key)


# opening the encrypted file
with open ('Government Dataset.csv', 'rb') as enc_Government_Dataset_file:
  encrypted = enc_Government_Dataset_file.read()


# decrypting the file
decrypted = fernet.decrypt(encrypted)


# opening the file in write mode and 
# writing the decrypted data
with open('Government Dataset.csv', 'wb') as dec_Government_Dataset_file:
  dec_Government_Dataset_file.write(decrypted)