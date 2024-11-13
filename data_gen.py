import pandas as pd
import numpy as np
import json
import random
from datetime import datetime
import singlestoredb as s2
import time

class GeospatialDatabaseInserter:
    def __init__(self, geospatial_data_path, db_url):
        self.geospatial_data = pd.read_csv(geospatial_data_path)
        self.person_profiles = self._generate_person_profiles()
        self.db_url = db_url  # Store the DB URL for later use

    def _generate_person_profiles(self):
        # Generate fixed profiles for up to 1 million people
        profiles = {}
        for person_id in range(1, 1000001):
            profiles[person_id] = {
                "person_id": person_id,
                "name": f"Person {person_id}",
                "age": random.randint(18, 80),
                "sex": random.choice(["Male", "Female"]),
                "reason_in_city": random.choice(["Tourism", "Business", "Resident", "Education"]),
                "job": random.choice(["Engineer", "Doctor", "Teacher", "None", None]),
                "ad_influence_score": round(random.uniform(0, 1), 2),
                "education_level": random.choice(["High School", "Bachelor Degree", "Master Degree", "PhD"]),
                "income_level": random.choice(["Low", "Middle", "High"]),
                "marital_status": random.choice(["Single", "Married", "Divorced"]),
            }
        return profiles

    def _generate_random_coordinates(self, base_lat, base_long):
        # Generate random coordinates around a base coordinate
        new_lat = np.random.normal(loc=base_lat, scale=0.01)
        new_long = np.random.normal(loc=base_long, scale=0.01)
        return [new_lat, new_long]

    def _generate_json_data(self, person_id, coordinates, timestamp):
        # Generate the data JSON object
        profile = self.person_profiles[person_id]
        profile.update({
            "geospatial_coordinates": coordinates,
            "timestamp": timestamp.isoformat()
        })
        return profile

    def insert_data(self, frequency_seconds=30):
        while True:
            try:
                # Select a random person ID and location
                person_id = random.randint(1, 1000000)
                chosen_location = self.geospatial_data.sample()
                base_lat, base_long = chosen_location['Latitude'].values[0], chosen_location['Longitude'].values[0]
                coordinates = self._generate_random_coordinates(base_lat, base_long)
                timestamp = datetime.now()

                # Generate JSON data for the person
                data_json = self._generate_json_data(person_id, coordinates, timestamp)

                # Convert the JSON data to a string format
                data_json_str = json.dumps(data_json)

                # Create a connection to the database
                conn = s2.connect(self.db_url)
                cur = conn.cursor()

                # Prepare the SQL insert statement
                insert_query = f"INSERT INTO person_details VALUES ('{data_json_str}')"

                # Print query for debugging (optional)
                print(f"Inserting JSON data: {data_json_str}")

                # Execute the insert statement
                cur.execute(insert_query)
                conn.commit()
                conn.close()

                print(f"Inserted: {data_json}")
                time.sleep(frequency_seconds)

            except Exception as e:
                # Print detailed error message
                print(f"Failed to insert data: {e}")