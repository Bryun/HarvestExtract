from pandas import DataFrame
from pdfplumber import open
from os import listdir, path
from os.path import splitext, split
from re import match, findall, compile, search, sub
from itertools import chain
from json import dump, dumps, load, loads
from numpy import array
from textractor import Textractor
from pdf2image import convert_from_path

source: str = "./Documents"

# location: str = f"{source}/2018_Bear_Harvest_by_method_and_county.pdf"

Bear_Harvest_by_method_and_county = (
    f"{source}/2018_Bear_Harvest_by_method_and_county.pdf"
)
Turkey_Harvest_County = f"{source}/2020-Turkey-Harvest-County.pdf"
NC_Deer_Harvest_By_Weapon_Type = (
    f"{source}/2022-2023-NC-Deer-Harvest-By-Weapon-Type.pdf"
)
Harv_GL18_1 = f"{source}/Harv_GL18_1.pdf"
Bear_Harvest_by_Game_Land_2008_2022 = (
    f"{source}/Bear-Harvest-by-Game-Land-2008-2022.pdf"
)
Bear_Harvest_by_Game_Land_2008_2022_Grey_Scale = (
    f"{source}/Bear-Harvest-by-Game-Land-2008-2022 (Grey-Scale).pdf"
)


def lines(location, start: int, end: int, heading: int, exclude: dict = []):
    """ """
    collection: list = []
    pageNo: int = 1

    with open(location) as reader:
        for page in reader.pages:
            content: str = page.extract_text()
            lines: list = content.split("\n")

            if pageNo == 1:
                collection.extend(lines[slice(start, len(lines))])
                pageNo += 1
            else:
                collection.extend(lines[slice(heading, len(lines))])

    for line in collection:
        print(line)

    return collection


def GetDataframe(rows, indexes: list):
    try:
        data = {}

        for y in range(len(rows)):
            for x in range(len(rows[y])):
                if y == 0:
                    if x in indexes:
                        data[rows[y][x]] = []
                else:
                    if x in indexes:
                        k = list(data.keys())
                        data[rows[0][x]].append(rows[y][x])
        return DataFrame.from_dict(data)
    except Exception:
        print(traceback.format_exc())

    return None


def partition(line: str, segments: list):
    collection: list = []
    expression = (
        " "
        if len(segments) == 0
        else r"|".join([f"({segment})" for segment in segments])
    )
    pattern = compile(expression)

    if search(pattern, line):
        located: list = findall(pattern, line)
        for x in located:
            collection.extend([y.strip() for y in x if y != ""])

    return collection


def structure(lines: list):
    scale: dict = {}

    for line in lines:
        word: str = line[0]
        scale[word] = len(line)

    print(dumps(scale, indent=4))


def test(name, page, extension=".png"):
    name: str = f"{name}_{page}{extension}"
    return name


def extract_text(path: str):

    # https://aws-samples.github.io/amazon-textract-textractor/index.html

    page = 1
    directory, file = split(path)
    name, extension = splitext(file)

    extractor: Textractor = Textractor(profile_name="guru-dev-profile")
    images = convert_from_path(
        path, fmt="png", output_folder="./Outputs/", paths_only=True, output_file=name
    )

    output: str = ''

    for image in images:
        document = extractor.start_document_text_detection(
            file_source=image,
            s3_upload_path='s3://ocr-harvest-extract-bucket/textractor/' 
        )

        output += document.text
    
    print(output)

    # with open(f'./Textual/{name}.txt', 'a+') as writer:
    #     writer.write(output)

# data = lines(Bear_Harvest_by_method_and_county, 1, -1, 3)
# rows = []

# for i in range(0, len(data)):
#     if i == 0:
#         rows.append(partition(data[i], ["Still", "Dog", "Percent Method"]))
#     elif i == 1:
#         rows.append(
#             partition(
#                 data[i],
#                 ["Male", "Female", "County total", "County", "Total", "Still", "Dog"],
#             )
#         )
#     else:
#         rows.append(partition(data[i], ["^\w+", "\d+%", "\d+", "N/A[0-9]{1,}", "N/A"]))

# structure(rows[slice(1, len(rows) - 1)])

# headers, lines = parameters(rows[slice(1, len(rows) - 1)])

# primary = DataFrame(rows[slice(2, len(rows) - 1)], columns=rows[1])
# print(primary.to_markdown())
# #----------------------------------------------------------
# still = partition(rows, [0, 1, 2, 3])
# print(still.to_markdown())
# print("\n\n\n")
# #----------------------------------------------------------
# dog = partition(rows, [0, 4, 5, 6])
# print(dog.to_markdown())
# print("\n\n\n")
# #----------------------------------------------------------
# percent_method = partition(rows, [0, 7, 8, 9])
# print(percent_method.to_markdown())
# print("\n\n\n")
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

# turkey_harvest_county = lines(Turkey_Harvest_County, 2, -1, 4)
# collection: list = []

# for i in range(len(turkey_harvest_county)):
#     if i == 0:
#         collection.append(partition(turkey_harvest_county[i], ['ADULT', 'TOTAL', 'GAME', 'OTHER', 'WRC']))
#     elif i == 1:
#         collection.append(partition(turkey_harvest_county[i], ['COUNTY', 'GOBBLERS', 'JAKES', 'TURKEYS', 'LANDS', 'DISTRICT', 'REGION']))
#     else:
#         collection.append(partition(turkey_harvest_county[i], ['^[\sA-Z]+', '[\d,]+', '\w+$']))

# for l in collection:
#     print(l)

# map: dict = {}

# for y in range(len(collection) - 1):
#     if y == 0:
#         for x in range(len(collection[y])):
#             map[collection[y][x]] = []
#     elif y == 1:
#         for x in range(len(collection[y])):
#             if x == 1:
#                 map[f'ADULT {collection[y][x]}'] = []
#                 del map['ADULT']
#             elif x == 3:
#                 map[f'TOTAL {collection[y][x]}'] = []
#                 del map['TOTAL']
#             elif x == 4:
#                 map[f'GAME {collection[y][x]}'] = []
#                 del map['GAME']
#             elif x == 5:
#                 map[f'OTHER {collection[y][x]}'] = []
#                 del map['OTHER']
#             elif x == 7:
#                 map[f'WRC {collection[y][x]}'] = []
#                 del map['WRC']
#             else:
#                 map[collection[y][x]] = []
#     else:
#         keys = list(map.keys())

#         for x in range(len(collection[y])):
#             map[keys[x]].append(collection[y][x].strip())

# data = DataFrame.from_dict(map)
# print(data.to_markdown())


# --------------------------------------------------------------------------------------------------------------------

# nc_deer_harvest_by_weapon_type = lines(
#     "./Documents/2022-2023-NC-Deer-Harvest-By-Weapon-Type.pdf", 1, -1, 3
# )
# collection: list = []

# for i in range(len(nc_deer_harvest_by_weapon_type)):
#     if i == 0:
#         collection.append(
#             partition(
#                 nc_deer_harvest_by_weapon_type[i],
#                 ["BOW", "CROSSBOW", "MUZZLELOADER", "GUN", "TOTAL"],
#             )
#         )
#     elif i == 1:
#         collection.append(
#             partition(
#                 nc_deer_harvest_by_weapon_type[i],
#                 ["DISTRICT", "COUNTY", "ANTLERED BUCK", "BUTTON BUCK", "DOE", "TOTAL"],
#             )
#         )
#     else:
#         collection.append(
#             partition(nc_deer_harvest_by_weapon_type[i], ["^\d", "[^\d]+[a-zA-Z]+\s[a-zA-Z]+[^\d]+", "[a-zA-Z]+", "[\d,]+"])
#         )

# collection[len(collection) - 1].insert(0, '')

# # for x in collection:
# #     print(f"{len(x)} --- {x}")

# rows = collection[slice(1, len(collection))]

# all = DataFrame(collection[slice(2, len(collection))], columns=collection[1])
# print(all.to_markdown())
# print("\n\n")

# bow = GetDataframe(rows, [0, 1, 2, 3, 4, 5])
# print(bow.to_markdown())
# print("\n\n")

# crossbow = GetDataframe(rows, [0, 1, 6, 7, 8, 9])
# print(crossbow.to_markdown())
# print("\n\n")

# muzzleloader = GetDataframe(rows, [0, 1, 10, 11, 12, 13])
# print(muzzleloader.to_markdown())
# print("\n\n")

# gun = GetDataframe(rows, [0, 1, 14, 15, 16, 17])
# print(gun.to_markdown())
# print("\n\n")

# total = GetDataframe(rows, [0, 1, 18, 19, 20, 21])
# print(total.to_markdown())


# # data = DataFrame.from_dict(map)
# # print(data.to_markdown())

# --------------------------------------------------------------------------------------------------------------------

# harv_gl18_1 = lines('.\Documents\Harv_GL18_1.pdf', 1, -1, 2)
# collection: list = []

# for i in range(len(harv_gl18_1)):
#     if i == 0:
#         collection.append(partition(harv_gl18_1[i], ['GAME LAND', 'ANTLERED BUCK', 'BUTTON BUCK', 'DOE', 'TOTAL']))
#     else:
#         collection.append(partition(harv_gl18_1[i], ['^[\sa-zA-Z.-]+', '[^ ]+']))

# for l in collection:
#     print(l)


# rows = collection

# white_tailed_deer = GetDataframe(rows, [0, 1, 2, 3, 4])
# print(white_tailed_deer.to_markdown())
# print("\n\n")

# --------------------------------------------------------------------------------------------------------------------


# bear_harvest_by_game_land_2008_2022 = lines('.\Documents\Bear-Harvest-by-Game-Land-2008-2022.pdf', 3, -1, 2)
# collection: list = []

# for i in range(len(bear_harvest_by_game_land_2008_2022)):
#     if i == 2:
#         collection.append(partition(bear_harvest_by_game_land_2008_2022[i], ['Game Land', 'Management Unit', '\d{4}', 'Total']))
#     else:
#         collection.append(partition(bear_harvest_by_game_land_2008_2022[i], ['^[ .\-/*a-zA-Z]+', '[\d,]+', '[ a-zA-Z]+$']))

# pattern = compile(r'Coastal BMU|Mountain BMU|Piedmont BMU|No Season|n/a')
# missing_space_pattern = compile(r'Other lands/Private/Unknown')

# for i in range(len(collection)):

#     l = collection[i]

#     # if l[0].startswith('Nantahala'):
#     #     print(l)

#     if len(l) > 0 and search(pattern, l[0]):
#         beacon = findall(pattern, l[0])
#         v = [sub(pattern, '', l[0]).strip()]
#         v.extend(beacon)
#         v.extend(l[slice(1, len(l))])
#         collection[i] = v
#     elif search(missing_space_pattern, l[0]):
#         v = [l[0].strip()]
#         v.extend([' '])
#         v.extend(l[slice(1, len(l))])
#         collection[i] = v

#     print(collection[i])

# scale: dict = {}
# for l in collection[slice(len(collection) - 1)]:
#     scale[l[0]] = len(l)

# print(dumps(scale, indent=4))


# map: dict = {}

# for y in range(1, len(collection) - 2):
#     if y == 1:
#         for x in range(len(collection[y])):
#             map[collection[y][x]] = []
#     if y == 2:
#         for x in range(len(collection[y])):
#             if x == 1:
#                 map[f'Bear {collection[y][x]}'] = []
#                 del map['Bear']
#             else:
#                 map[collection[y][x]] = []
#     else:
#         keys = list(map.keys())

#         for x in range(len(collection[y])):
#             map[keys[x]].append(collection[y][x].strip())

# data = DataFrame.from_dict(map)
# print(data.to_markdown())


# for file in listdir('./Documents'):
#     if file.endswith('.pdf'):
#         print(f"\n\nFILENAME: {file.title()}\n\n")
#         name, extension = splitext(file.title())

#         with open(path.join('./Documents/', file)) as reader:
#             for page in reader.pages:
#                 image = page.to_image()
#                 image.save(f'./Images/{name}.png', format='PNG')
#                 break


extract_text(Bear_Harvest_by_method_and_county)
