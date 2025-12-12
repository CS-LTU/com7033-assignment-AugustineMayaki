import random
import pandas as pd
from faker import Faker

def generate_fake_demographics(input_file="csv/healthcare_dataset_stroke_data.csv", nrows=1000):
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    df = pd.read_csv(input_file)
    df = df.head(nrows)

    first_names = []
    last_names = []
    emails = []

    for g in df["gender"]:
        g = str(g).strip().lower()
        if g == "male":
            first_name = fake.first_name_male()
        elif g == "female":
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name()
        last_name = fake.last_name()
        number = random.randint(10, 9999)
        email = f"{first_name.lower()}.{last_name.lower()}{number}@example.com"
        first_names.append(first_name)
        last_names.append(last_name)
        emails.append(email)

    df["first_name"] = first_names
    df["last_name"] = last_names
    df["email"] = emails
    return df

# If run as a script, create and save the fake demographics CSV
if __name__ == "__main__":
    output_file = "csv/healthcare_dataset_stroke_with_names.csv"
    df = generate_fake_demographics()
    df.to_csv(output_file, index=False)
    print("Saved file with fake names/emails as:", output_file)
