import os
import google.oauth2.credentials
import sys
# import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import argparser, run_flow
# from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies
# the name of a file that contains
# client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

# This scope allows for full read/write access
# to the authenticated user's account and requires
# requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    # flow = InstalledAppFlow.from_client_secrets_file(
    #                      CLIENT_SECRETS_FILE, SCOPES)
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=SCOPES,
                                   message="failed no secretsFile")

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def print_response(response):
    print(response)

# Build a resource based on a list of properties
# given as key-value pairs. Leave properties with
# empty values out of the inserted resource.


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into
        # "snippet" and "title", where "snippet" will be
        # an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

        # For properties that have array values,
        # convert a name like "snippet.tags[]" to
        # snippet.tags, and set a flag to handle
        # the value as an array.
        if key[-2:] == '[]':
            key = key[0:len(key)-2:]
            is_array = True

        if pa == (len(prop_array) - 1):
            # Leave properties without values
            # out of inserted resource.
            if properties[p]:
                if is_array:
                    ref[key] = properties[p].split(',')
                else:
                    ref[key] = properties[p]
        elif key not in ref:
            # For example, the property is "snippet.title",
            # but the resource does not yet have a "snippet"
            # object. Create the snippet object here.
            # Setting "ref = ref[key]" means that in the next
            # time through the "for pa in range ..." loop, we
            # will be setting a property in the
            # resource's "snippet" object.
            ref[key] = {}
            ref = ref[key]
        else:
            # For example, the property is "snippet.description",
            # and the resource already has a "snippet" object.
            ref = ref[key]
    return resource

# Remove keyword arguments that are not set


def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def playlist_items_insert(client, properties, **kwargs):
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.playlistItems().insert(
        body=resource, **kwargs).execute()

    return print_response(response)


def main(playlistId, videoId):

    # When running locally, disable OAuthlib's HTTPs
    # verification. When running in production *do not*
    # leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    client = get_authenticated_service()

    playlist_items_insert(client,
                          {'snippet.playlistId': playlistId,
                           'snippet.resourceId.kind': 'youtube#video',
                           'snippet.resourceId.videoId': videoId,
                           'snippet.position': ''},
                          part='snippet',
                          onBehalfOfContentOwner='')
