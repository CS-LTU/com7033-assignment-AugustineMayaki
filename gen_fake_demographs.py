import random
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

input_file = "csv/healthcare_dataset_stroke_data.csv"              
output_file = "csv/healthcare_dataset_stroke_with_names.csv" 

# read input csv
df = pd.read_csv(input_file)

# ✅ Slice data to first 1000 rows
df = df.head(1000)  

# Gets ready lists for new columns
first_names = []
last_names = []
emails = []

for g in df["gender"]:
    
    """
    Generate fake first name, last name, and email based on gender
    
    """
    g = str(g).strip().lower()

    if g == "male":
        first_name = fake.first_name_male()
    elif g == "female":
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name()  

    last_name = fake.last_name()

    # Generate email
    number = random.randint(10, 9999)
    email = f"{first_name.lower()}.{last_name.lower()}{number}@example.com"

    # Append to lists
    first_names.append(first_name)
    last_names.append(last_name)
    emails.append(email)

# add new columns
df["first_name"] = first_names
df["last_name"] = last_names
df["email"] = emails

# save new csv
df.to_csv(output_file, index=False)
print("Saved file with fake names/emails as:", output_file)
