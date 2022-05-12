import json
import shutil

import requests
import os
import wget

def load_json(json_path):
    moodle_file = open(json_path)
    moodle_json = json.load(moodle_file)
    return moodle_json

def extract_dates_and_files(moodle_json):
    assignments = []
    for assignment in moodle_json:
        cur_assign_dict = {}
        cur_assign_dict["course"] = assignment["fullname"]
        cur_assign_dict["assignment_name"] = assignment["files"][0]["filename"].split(".")[0]
        cur_assign_dict["due_date"] = assignment["enddate"]
        pdf_path = download_pdf(assignment["files"][0]["fileurl"],cur_assign_dict["assignment_name"])
        cur_assign_dict["pdf_path"] = pdf_path
        assignments.append(cur_assign_dict)

    return assignments

def download_pdf(url, file_name):
    path = os.path.join("{}/{}".format(os.path.dirname(__file__), file_name))
    req = requests.get(url)
    with open("{}.pdf".format(file_name), 'wb') as pdf:
        pdf.write(req.content)

    return path


if __name__ == "__main__":
    moodle_json = load_json("moodle_output.json")
    assignments = extract_dates_and_files(moodle_json)
    print(assignments)




