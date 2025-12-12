"""
Reset the database seeding flag.
Run this script to allow init_database() to re-seed the database on next app start.
"""
import os

seed_flag_file = os.path.join('instance', '.db_seeded')

if os.path.exists(seed_flag_file):
    os.remove(seed_flag_file)
    print("Seed flag removed. Database will re-seed on next app start.")
else:
    print("No seed flag found. Database will seed on next app start.")
