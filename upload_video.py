#Upload video program
#Heavy inspiration from https://developers.google.com/youtube/v3/guides/uploading_a_video

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


def get_authenticated_service(args):
  flow = flow_from_clientsecrets("client_secrets.json", scope="https://www.googleapis.com/auth/youtube.upload")

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build("youtube", "v3", http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Upload video
  insert_request = youtube.videos().insert(
    part=",".join(list(body.keys())),
    body=body,
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  print("Upload Started")
  insert_request.next_chunk()
  print("File Uploaded")

#Parse arguments
if __name__ == '__main__':
  argparser.add_argument("--file", required=True)
  argparser.add_argument("--title", default="Test Title")
  argparser.add_argument("--description", default="Test Description")
  argparser.add_argument("--category", default="22")
  argparser.add_argument("--keywords", default="")
  argparser.add_argument("--privacyStatus", choices=("public", "private"), default="public")
  args = argparser.parse_args()

  if not os.path.exists(args.file):
    exit("Invalid File")

  youtube = get_authenticated_service(args)
  initialize_upload(youtube, args)