import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
import re


def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())


def similarity_ratio(a, b):
    return SequenceMatcher(None, preprocess_text(a), preprocess_text(b)).ratio()


def insert_fact(cursor, fact, category, source, tags, author):
    cursor.execute('SELECT id, fact FROM fun_facts')
    existing_facts = cursor.fetchall()

    for existing_id, existing_fact in existing_facts:
        similarity = similarity_ratio(fact, existing_fact)
        if similarity > 0.7:  # You can adjust this threshold
            print(f"\nPotential duplicate detected:")
            print(f"New fact: {fact}")
            print(f"Existing fact (ID {existing_id}): {existing_fact}")
            print(f"Similarity: {similarity:.2f}")

            choice = input("Do you want to insert this fact anyway? (y/n): ").lower()
            if choice != 'y':
                print("Fact discarded.")
                return False

    cursor.execute('''
    INSERT INTO fun_facts (fact, category, source, tags, author) 
    VALUES (?, ?, ?, ?, ?)
    ''', (fact, category, source, tags, author))
    return True


conn = sqlite3.connect('fun_facts.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS fun_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact TEXT NOT NULL,
    category TEXT,
    source TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language TEXT DEFAULT 'en',
    tags TEXT,
    author TEXT
)
''')

new_fun_facts = [
    ("The coldest temperature ever recorded on Earth was -128.6°F at the Soviet Union’s Vostok Station in Antarctica.", "Weather", "World Meteorological Organization", "coldest, temperature, Antarctica", "admin"),
    ("Lightning can reach temperatures of up to 30,000 K, which is five times hotter than the surface of the sun.", "Weather", "National Weather Service", "lightning, temperature, sun", "admin"),
    ("The highest speed of a raindrop is about 18 mph.", "Weather", "National Geographic", "raindrop, speed, weather", "admin"),
    ("In 1816, there was a year without a summer due to a volcanic eruption at Mount Tambora in Indonesia.", "Weather", "Smithsonian", "year without summer, volcano, eruption", "admin"),
    ("A cubic mile of fog is made up of less than a gallon of water.", "Weather", "Weather Encyclopedia", "fog, volume, weather", "admin"),
    ("Hurricanes can release as much energy as 10,000 nuclear bombs.", "Weather", "NOAA", "hurricane, energy, weather", "admin"),
    ("A cloud can weigh over a million pounds.", "Weather", "BBC Weather", "cloud, weight, atmosphere", "admin"),
    ("The deadliest weather disaster in history was the 1931 China floods, killing between 1 to 4 million people.", "Weather", "History Channel", "flood, China, disaster", "admin"),
    ("The strongest wind speed ever recorded was 253 mph during Tropical Cyclone Olivia in 1996.", "Weather", "World Meteorological Organization", "wind speed, cyclone, Olivia", "admin"),
    ("The Sahara Desert, one of the hottest places on Earth, has recorded snowfall.", "Weather", "NASA", "Sahara, desert, snowfall", "admin"),
    ("The Great Smog of London in 1952 killed over 12,000 people due to toxic fog.", "Weather", "British History Journal", "smog, London, fog", "admin"),
    ("A single bolt of lightning contains enough energy to cook 100,000 pieces of toast.", "Weather", "National Weather Service", "lightning, energy, weather", "admin"),
    ("Snowflakes can take up to an hour to fall from the cloud to the ground.", "Weather", "Weather.com", "snowflake, time, weather", "admin"),
    ("Earth experiences about 100 lightning strikes every second.", "Weather", "National Weather Service", "lightning, strikes, Earth", "admin"),
    ("In the tropics, a weather phenomenon known as 'thundersnow' involves lightning occurring during a snowstorm.", "Weather", "NOAA", "thundersnow, lightning, snowstorm", "admin"),
    ("Antarctica is the driest, coldest, and windiest continent on Earth.", "Weather", "National Geographic", "Antarctica, driest, coldest, windiest", "admin"),
    ("On average, a tornado lasts less than 10 minutes.", "Weather", "Tornado Facts", "tornado, duration, weather", "admin"),
    ("The largest hailstone recorded in the U.S. fell in South Dakota in 2010, weighing nearly two pounds.", "Weather", "National Weather Service", "hailstone, South Dakota, weather", "admin"),
    ("The highest temperature ever recorded on Earth was 134°F in Death Valley, California.", "Weather", "National Geographic", "temperature, Death Valley, record", "admin"),
    ("Tsunamis can travel across the ocean at speeds of up to 500 miles per hour.", "Weather", "NOAA", "tsunami, speed, weather", "admin"),
    ("The largest sandstorm on record occurred in China in 2001, stretching over 2000 miles.", "Weather", "Weather.com", "sandstorm, China, record", "admin"),
    ("The Ozone Hole is largest in September and October due to chemical reactions in polar stratospheric clouds.", "Weather", "NASA", "ozone hole, stratospheric clouds, weather", "admin"),
    ("Hawaii holds the world record for the most rainfall in one year, receiving over 467 inches in 1982.", "Weather", "World Meteorological Organization", "rainfall, Hawaii, record", "admin"),
    ("Clouds that appear as UFO-shaped disks are called lenticular clouds and form in mountainous regions.", "Weather", "BBC Weather", "lenticular clouds, UFO, weather", "admin"),
    ("The world’s smallest active tornado was just over three feet tall.", "Weather", "Tornado Facts", "tornado, size, weather", "admin"),

    ("In Georgia, it's illegal to eat fried chicken with anything other than your hands.", "Weird Laws", "Georgia State Legislature", "fried chicken, hands, law", "admin"),
    ("In Switzerland, it's illegal to own just one guinea pig because they are prone to loneliness.", "Weird Laws", "Swiss Animal Welfare Law", "guinea pig, loneliness, law", "admin"),
    ("In California, it's illegal for a woman to drive while wearing a housecoat.", "Weird Laws", "California State Law", "housecoat, driving, law", "admin"),
    ("In France, it's illegal to name a pig 'Napoleon.'", "Weird Laws", "French Law", "pig, Napoleon, law", "admin"),
    ("In New York, it's illegal to wear slippers after 10 p.m.", "Weird Laws", "New York City Ordinance", "slippers, time, law", "admin"),
    ("In Australia, it's illegal to disrupt a wedding or a funeral, with fines exceeding $10,000.", "Weird Laws", "Australian Law", "wedding, funeral, disruption, law", "admin"),
    ("In Victoria, Australia, it is illegal to change a light bulb unless you are a licensed electrician.", "Weird Laws", "Victoria State Law", "light bulb, electrician, law", "admin"),
    ("In Samoa, it's illegal to forget your wife's birthday.", "Weird Laws", "Samoan Law", "birthday, wife, law", "admin"),
    ("In Florida, if an elephant is left tied to a parking meter, the owner must pay the meter as if it were a car.", "Weird Laws", "Florida State Law", "elephant, parking meter, law", "admin"),
    ("In Kentucky, it's illegal to carry ice cream in your back pocket.", "Weird Laws", "Kentucky State Law", "ice cream, pocket, law", "admin"),
    ("In Milan, Italy, it's a legal requirement to smile at all times, except during funerals or hospital visits.", "Weird Laws", "Milan City Law", "smile, legal requirement, law", "admin"),
    ("In Vermont, women need written permission from their husbands to wear false teeth.", "Weird Laws", "Vermont State Law", "false teeth, permission, law", "admin"),
    ("In Oklahoma, it's illegal to make ugly faces at a dog.", "Weird Laws", "Oklahoma State Law", "dog, ugly face, law", "admin"),
    ("In Canada, it's illegal to scare the queen.", "Weird Laws", "Canadian Law", "queen, scare, law", "admin"),
    ("In Scotland, if someone knocks on your door and requests to use the bathroom, you must let them in.", "Weird Laws", "Scottish Law", "bathroom, entry, law", "admin"),
    ("In Japan, it is illegal to be overweight.", "Weird Laws", "Japanese Law", "overweight, law, Japan", "admin"),
    ("In Singapore, chewing gum is strictly regulated and only allowed for medical purposes.", "Weird Laws", "Singapore Law", "chewing gum, law, regulation", "admin"),
    ("In Missouri, it's illegal to drive with an uncaged bear in your car.", "Weird Laws", "Missouri State Law", "bear, car, law", "admin"),
    ("In South Korea, traffic violations by cats and dogs are finable offenses.", "Weird Laws", "South Korean Law", "cats, dogs, traffic violations", "admin"),
    ("In Texas, it's illegal to sell your eye.", "Weird Laws", "Texas State Law", "eye, sell, law", "admin"),
    ("In Alaska, you can’t wake a sleeping bear to take a picture.", "Weird Laws", "Alaska State Law", "bear, wake, law", "admin"),
    ("In Washington, it's illegal to harass Bigfoot.", "Weird Laws", "Washington State Law", "Bigfoot, harass, law", "admin"),
    ("In Illinois, it's illegal to eat in a burning building.", "Weird Laws", "Illinois State Law", "eat, burning building, law", "admin"),
    ("In Idaho, it's illegal to give your sweetheart a box of chocolates weighing more than 50 pounds.", "Weird Laws", "Idaho State Law", "chocolates, sweetheart, law", "admin"),
    ("In Japan, it is illegal to put ice cream in the mailbox.", "Weird Laws", "Japanese Law", "ice cream, mailbox, law", "admin")
]




inserted_count = 0
for fact, category, source, tags, author in new_fun_facts:
    if insert_fact(cursor, fact, category, source, tags, author):
        inserted_count += 1

conn.commit()
conn.close()

print(f"{inserted_count} new fun facts have been added to the database, yo!")