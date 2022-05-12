from fileinput import filename
from turtle import down
import driveaccess
import io
from googleapiclient.http import MediaIoBaseDownload

def downloadFile(drive_service, file):
    request = drive_service.files().get_media(fileId=file['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with open("{}".format(file['name']), "wb") as f:
        f.write(fh.getbuffer())

def search_files(drive_service):
    service = drive_service
    page_token = None
    total_files = []
    while True:
        query = "mimeType='application/pdf'"
        response = service.files().list(q=query,
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)',
                                          pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            total_files.append(file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

search_files(driveaccess.access_drive())
    

        
