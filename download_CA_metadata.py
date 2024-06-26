#!/bin/env python3
import requests
import pandas
import pwinput

session_token = pwinput.pwinput(prompt='Please enter your CA session token: ', mask='*')

url = f"https://champions.io/api/inventory/{session_token}"

def getData(type):
  items=list()
  cursor = None
  counter=0
  while cursor != "":
    counter+=1
    print(f"Loading page {counter}")
    cursor_text=""
    if cursor:
        cursor_text=f', "cursor" : "{cursor}"'
    
    data=f'{{"collectionTypes":"{type}"{cursor_text}}}'
    response = requests.post(url, data=data)

    if response.status_code>300: 
      print(data)
      print(response.text)
    value = response.json()
    for item in value["items"]:
      items.append(item)
    cursor = value["cursor"]
  return items

def getAttributes(items, additionalKeys=[]):
  attributes = list()
  for item in items:
    obj = {}
    for attribute in item['attributes']:
      key = attribute['traitType']
      value = attribute['value']
      obj[key] = value
    for key in additionalKeys:
      obj[key] = item[key]
    attributes.append(obj)
  return attributes

print("fetching scroll data")
items = getData("ascensionScrolls")
scrolls = getAttributes(items)

if scrolls:
  values=["Tier","Inscription"]
  df = pandas.DataFrame(scrolls) 
  df.groupby(values).size().to_frame('Count').reset_index().sort_values(["Tier", "Count"], ascending=False).to_csv("scrolls.csv", index=False)
  print("scroll data written to scrolls.csv")

print("fetching gallery data")
items = getData("imperialGallery")
gallery = getAttributes(items, ["tokenName"])

if gallery:
  df = pandas.DataFrame(gallery).rename(columns={"tokenName" : "Name"})
  df['Name'] = df['Name'].replace('(.*?)\w\d*/\d*', r"\1", regex=True)
  df = df.groupby(["Name", "Category", "Collection"]).size().to_frame('Count')
  df.reset_index().sort_values("Count", ascending=False).to_csv("gallery.csv", index=False)
  print("gallery data written to gallery.csv")

print("fetching monster parts data")
items = getData("monstrousCompendium")
monster_parts = getAttributes(items)

if monster_parts:
  values=["Rarity", "Piece", "Type", "Collection"]
  df = pandas.DataFrame(monster_parts) 
  df.groupby(values).size().to_frame('Count').reset_index().sort_values(values).to_csv("monster_parts.csv", index=False)
  print("monster parts data written to monster_parts.csv")

  print("fetching crystal data")
  items = getData("crystals")
  crystals = getAttributes(items)

if crystals:
  values=["Rarity", "Size", "Glow", "House", "Essence", "Modifier", "Crystal 1 Size", "Crystal 2 Size", "Crystal 3 Size", "Crystal 4 Size"]
  df = pandas.DataFrame(crystals).rename(columns={"Number of Crystals" : "Size", "Essence Value" : "Essence"})
  for cs in ["Crystal 2 Size", "Crystal 3 Size", "Crystal 4 Size"]: 
    df[cs] = df[cs].replace("None", "")
  df[values].sort_values(["Size", "Essence"], ascending=False, key=pandas.to_numeric).to_csv("crystals.csv", index=False)
  print("monster parts data written to crystals.csv")

print("fetching pet data")
items = getData("pets")
pets = getAttributes(items, ["tokenId"])

if pets:
  values=["ID", "Family","Edition", "Favorite Family", "House Banner","Personality","Favorite Toy","Favorite Food"]
  df = pandas.DataFrame(pets).rename(columns={"tokenId" : "ID"})
  df[values].sort_values(["ID"], key=pandas.to_numeric).to_csv("pets.csv", index=False)
  print("pet data written to pets.csv")

print("fetching champion data")
items = getData("allChampions")
champs = getAttributes(items, ["tokenId", "essence", "totalEssence", "level", "xp", "isDead"])

eternals=[]
gladiators=[]
challengers=[]
grunts=[]

ascensions = {
  "Eternal" : eternals,
  "Gladiator" : gladiators,
  "Challenger" : challengers,
  "Grunt" : grunts
}

for champ in champs:
  ascensions[champ['Ascension']].append(champ)
  
if eternals:
  values=["ID", "Edition", "Divinity", "Sublime", "Purity", "Family", "Essence", "Claws", "Fangs", "Horns", "Tail", "Warpaint", "Wings", "Total Essence", "Level", "XP", "Class","Halo", "Piercing","Hairstyle"]
  df = pandas.DataFrame(eternals).rename(columns={"tokenId" : "ID", "essence" : "Essence", "totalEssence" : "Total Essence", "level" : "Level", "xp" : "XP", "Core Essence" : "Essence"})
  df[values].sort_values(["Divinity", "Sublime", "Purity"], ascending=False).to_csv("eternals.csv", index=False)
  print("champion data written to eternals.csv")

if gladiators:
  values=["ID",  "Level", "XP", "Purity", "Family", "Essence", "Claws", "Fangs", "Horns", "Tail", "Warpaint", "Wings",  "Total Essence", "Status", "Rating","Class","Piercing","Hairstyle"]
  df = pandas.DataFrame(gladiators).rename(columns={"tokenId" : "ID", "essence" : "Essence", "totalEssence" : "Total Essence", "level" : "Level", "xp" : "XP", "isDead": "Status", "Core Essence" : "Essence"})
  df["Status"] = df["Status"].replace("False", "Alive")
  df["Status"] = df["Status"].replace("True", "Dead")
  df[values].sort_values(["Rating", "XP", "Purity"], ascending=False).to_csv("gladiators.csv", index=False)
  print("champion data written to gladiators.csv")

if challengers:
  values=["ID",  "Level", "XP", "Purity", "Family", "Essence", "Claws", "Fangs", "Horns", "Tail", "Warpaint", "Wings",  "Total Essence", "Status", "Rating","Class","Piercing","Hairstyle"]
  df = pandas.DataFrame(challengers).rename(columns={"tokenId" : "ID", "essence" : "Essence", "totalEssence" : "Total Essence", "level" : "Level", "xp" : "XP", "isDead": "Status", "Core Essence" : "Essence"})
  df["Status"] = df["Status"].replace("False", "Alive")
  df["Status"] = df["Status"].replace("True", "Dead")
  df[values].sort_values(["Rating", "XP", "Purity"], ascending=False).to_csv("challengers.csv", index=False)
  print("champion data written to challengers.csv")

if grunts:
  values=["ID",  "Level", "XP", "Family", "Essence", "Rarity", "Fangs", "Tail", "Wings", "Warpaint", "Horns", "Claws", "House Affinity", "Total Essence", "Status", "Rating", "Class","Piercing","Hairstyle"]
  df = pandas.DataFrame(grunts).rename(columns={"tokenId" : "ID", "essence" : "Essence", "totalEssence" : "Total Essence", "level" : "Level", "xp" : "XP", "isDead": "Status", "Guaranteed Fangs" : "Fangs", "Guaranteed Tail" : "Tail", "Guaranteed Wings" : "Wings", "Guaranteed Warpaint" : "Warpaint", "Guaranteed Horns" : "Horns", "Guaranteed Claws" : "Claws",})
  df["Status"] = df["Status"].replace("FALSE", "Alive")
  df["Status"] = df["Status"].replace("TRUE", "Dead")
  df[values].sort_values(["Rarity"], ascending=False).to_csv("grunts.csv", index=False)
  print("champion data written to champions.csv")