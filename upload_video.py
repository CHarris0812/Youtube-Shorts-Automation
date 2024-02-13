#Upload video program
#Heavy inspiration from https://developers.google.com/youtube/v3/guides/uploading_a_video

import httplib2
import os

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from argparse import Namespace

class videoUploader():
  args = Namespace()

  def __init__(self):
    self.args.auth_host_name = 'localhost'
    self.args.noauth_local_webserver = False
    self.args.auth_host_port = [8080, 8090]
    self.args.logging_level="ERROR"

  def upload(self, file, title = "Untitled Video", description = "", category = "22", keywords = "", privacyStatus = "public"):
    if not os.path.exists(file):
      exit("Invalid File")

    self.args.file = file
    self.args.title = title
    self.args.description = description
    self.args.category = category
    self.args.keywords = keywords
    self.args.privacyStatus = privacyStatus 

    print(self.args) 
    youtube = self.get_authenticated_service()
    self.initialize_upload(youtube)

  def get_authenticated_service(self):
    flow = flow_from_clientsecrets("client_secrets.json", scope="https://www.googleapis.com/auth/youtube.upload")

    storage = Storage("%s-oauth2.json" % "upload_video.py")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      credentials = run_flow(flow, storage, self.args)

    return build("youtube", "v3", http=credentials.authorize(httplib2.Http()))

  def initialize_upload(self, youtube):
    tags = None
    if self.args.keywords:
      tags = self.args.keywords.split(",")

    body=dict(
      snippet=dict(
        title=self.args.title,
        description=self.args.description,
        tags=tags,
        categoryId=self.args.category
      ),
      status=dict(
        privacyStatus=self.args.privacyStatus
      )
    )

    # Upload video
    insert_request = youtube.videos().insert(
      part=",".join(list(body.keys())),
      body=body,
      media_body=MediaFileUpload(self.args.file, chunksize=-1, resumable=True)
    )

    print("Upload Started")
    insert_request.next_chunk()
    print("File Uploaded")

#Parse arguments
if __name__ == '__main__':
  myUploader = videoUploader()
  myUploader.upload("Test.mp4", title="Testing as class")