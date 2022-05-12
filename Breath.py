import json
import requests
import os
from Constants import *
from difflib import SequenceMatcher
import tika, re
from tika import parser
from collections import Counter
from fileinput import filename
from turtle import down
import driveaccess
import io
from googleapiclient.http import MediaIoBaseDownload


### Adi's backend code

def load_json(json_path):
    moodle_file = open(json_path)
    moodle_json = json.load(moodle_file)
    return moodle_json


def extract_dates_and_files(moodle_json):
    assignments = []
    for assignment in moodle_json:
        cur_assign_dict = {}
        cur_assign_dict[COURSE] = assignment["fullname"]
        cur_assign_dict[ASSIGNMENT_NAME] = assignment["files"][0]["filename"].split(".")[0]
        cur_assign_dict[DUE_DATE] = assignment["enddate"]
        pdf_path = download_pdf(assignment["files"][0]["fileurl"], cur_assign_dict[ASSIGNMENT_NAME])
        cur_assign_dict[PDF_PATH] = pdf_path
        assignments.append(cur_assign_dict)

    return assignments


def download_pdf(url, file_name):
    path = os.path.join("{}\{}".format(os.path.dirname(__file__),file_name+".pdf"))
    req = requests.get(url)
    with open("{}.pdf".format(file_name), 'wb') as pdf:
        pdf.write(req.content)

    return path


#Nir and Slutzky backend



def find_noisy_words(path):
        word_counts = dict()
        for f in os.listdir(path): ## for f in drive
            # f downloadr(path)
            parsed = parser.from_file(path + f)
            c = Counter(parsed["content"].replace('\n',"").split(" "))
            for word in c:
                if word not in word_counts:
                    word_counts[word] = 0
                word_counts[word] += c[word]
        bar = 10 ## Rethink?
        return [word for word in word_counts if word_counts[word] > bar]

def clean(text, noisy_words):
    text = [x.split(" ") for x in text if len(x)>=20]
    text = [[w for w in x if w not in noisy_words] for x in text]
    text = [[w for w in x if w != ''] for x in text]
    return text

def parse(path, noisy_words):
    parsed = tika.parser.from_file(path)
    text = re.split('שאלה|תשובה', parsed["content"].replace('\n',""))
    return clean(text, noisy_words)

def find_score(new_pdf_lst, old_pdf_lst): # Return score of old_pdf_lst
    scores = [0 for i in range(len(new_pdf_lst))]
    for i, new_sent in enumerate(new_pdf_lst):
        for old_sent in old_pdf_lst:
            if SequenceMatcher(None, new_sent, old_sent).ratio() > 0.5:
                scores[i] += 1
                break
    return sum(scores) / len(scores)


# nitzan backend



def downloadFile(drive_service, file, index , all_files_in_drive):
    request = drive_service.files().get_media(fileId=file['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with open("./pdfs/{}".format(file['name']), "wb") as f:
        f.write(fh.getbuffer())
    all_files_in_drive[index]['path'] = "./{}".format(file['name'])


def search_files(drive_service):
    service = drive_service
    page_token = None
    total_files = []
    while True:
        query = "mimeType='application/pdf' and trashed=false"
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name, webViewLink)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            total_files.append(file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return total_files



if __name__ == "__main__":
    driveservice = driveaccess.access_drive()
    all_files_in_drive = search_files(driveservice)
    for index, file in enumerate(all_files_in_drive):
        downloadFile(driveservice, file, index, all_files_in_drive)

    moodle_json = load_json("moodle_output.json")
    assignments = extract_dates_and_files(moodle_json)

    tika.initVM()
    for assignment in assignments:
        new_assignment_path = assignment[PDF_PATH]
        old_assignments_path = "D:\Studies\Bachelor Degree\\2022-Hackathon\pdfs\\" #integrate with Nitzan
        noisy_words = find_noisy_words(old_assignments_path)
        new_pdf_lst = parse(new_assignment_path, noisy_words)

        urls = []
        scores = []
        for f in all_files_in_drive:
            urls.append(f['webViewLink'])
            old_pdf_lst = parse(old_assignments_path + f['path'], noisy_words)
            scores.append(find_score(new_pdf_lst, old_pdf_lst))
        avg_score = sum(scores) / len(scores)
        significant = [(urls[i], scores[i]) for i in range(len(scores)) if scores[i] > 0]
        significant.sort(key=lambda x: x[1], reverse=True)

        assignment["Coverage"] = sum([x[1] for x in significant])*100
        links = "".join([x[0] for x in significant])
        assignment["ref_url"] = links




    apiUrl = "https://api.monday.com/v2"
    myToken = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE2MDE3MDU1OSwidWlkIjoyOTk1NzE5NCwiaWFkIjoiMjAyMi0wNS0xMlQwODoxODoyOS4xMDZaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTE4NzU5MjIsInJnbiI6InVzZTEifQ.kvSNJQ9B9TrWUI_BX8Z9B2Vg0x6PSaLBW3cxp7wRi-Y"
    apiKey = myToken
    headers = {"Authorization": apiKey}
    boardId = "2663367465"

    # Fields to be received from code, placeholders for now
    for assignment in assignments:
        toMonday = {'assignment_name': assignment[ASSIGNMENT_NAME],
                    'due_date': assignment[DUE_DATE],
                    'ref_url': assignment["ref_url"],
                    'coverage': int(assignment[COVERAGE])}

        query = 'mutation ($myItemName: String!, $columnVals: JSON!) { create_item (board_id:2663367465, ' \
                'item_name:$myItemName, column_values:$columnVals) { id } } '
        vars = {
            'myItemName': 'Computer Architecture - '+toMonday["assignment_name"],
            'columnVals': json.dumps({
                'status': {'label': 'Working on it'},
                'date4': {'date': toMonday['due_date']},
                'text': toMonday['ref_url'],
                'numbers': toMonday['coverage']
            })
        }
        data = {'query': query, 'variables': vars}
        r = requests.post(url=apiUrl, json=data, headers=headers)  # make request
        print(r.json())