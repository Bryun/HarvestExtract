import traceback

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
from PIL import Image
from textractor.data.constants import TextractFeatures, Direction, DirectionalFinderType
from textractor.visualizers.entitylist import EntityList

source: str = "./Documents"



def lines(location):
    """ """
    collection: list = []
    pageNo: int = 1

    with open(location) as reader:
        for page in reader.pages:
            content: str = page.extract_text()
            lines: list = content.split("\n")
            collection.extend(lines)
            pageNo += 1

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


def convert_pdf_to_image(path: str):
    for file in listdir(path):
        if file.endswith('.pdf'):
            print(f"\n\nFILENAME: {file.title()}\n\n")
            name, extension = splitext(file.title())

            with open(path.join(path, file)) as reader:
                for page in reader.pages:
                    image = page.to_image()
                    image.save(f'./Images/{name}.png', format='PNG')
                    break
                

def extract_table(path: str):
    directory, file = split(path)
    name, extension = splitext(file)

    extractor: Textractor = Textractor(profile_name="guru-dev-profile")
    images = convert_from_path(
        path, fmt="png", output_folder="./Outputs/", paths_only=True, output_file=name
    )
    for image in images:
        document = extractor.analyze_document(
            file_source=image,
            features=[TextractFeatures.TABLES],
            save_image=True
            # s3_upload_path='s3://ocr-harvest-extract-bucket/textractor/',
        )

        table = EntityList(document.tables[0])
        document.tables[0].visualize()

        table[0].to_pandas()

def extract_forms(path: str):
    directory, file = split(path)
    name, extension = splitext(file)

    extractor: Textractor = Textractor(profile_name="guru-dev-profile")
    images = convert_from_path(
        path, fmt="png", output_folder="./Outputs/", paths_only=True, output_file=name
    )
    for image in images:
        document = extractor.start_document_analysis(
            file_source=Image.open(image),
            features=[TextractFeatures.FORMS],
            save_image=True,
            s3_upload_path='s3://ocr-harvest-extract-bucket/textractor/',
        )

        print(document.key_values)

extract_forms('./Documents/The Dent Center (Application).pdf')
