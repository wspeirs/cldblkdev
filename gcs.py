import json
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from googleapiclient import discovery
from googleapiclient import http
from googleapiclient import errors
from io import BytesIO


DEFAULT_BUCKET = 'blkdev_1'
RETRYABLE_ERRORS = (httplib2.HttpLib2Error, IOError)
MAX_RETRIES = 5
KB_4 = 4 * 1024


def get_gcs():
    """
    Gets a handle to the Google Cloud Storage service
    :return: handle to be used in subsequent calls
    """
    with open('cloud_backup_secret.json') as f:
        secrets = json.load(f)

    credentials = SignedJwtAssertionCredentials(secrets['client_email'],
                                                secrets['private_key'],
                                                'https://www.googleapis.com/auth/devstorage.read_write')

    authed_http = credentials.authorize(Http())

    return discovery.build('storage', 'v1', http=authed_http)


def list(gcs, bucket=DEFAULT_BUCKET):
    """
    Returns a list of all of the sectors found in the bucket
    :param gcs: handle to the Google Cloud Storage service
    :param bucket: optional bucket name
    :return: list of sectors in the bucket
    """
    ret = []

    json = gcs.objects().list(bucket=bucket, projection='noAcl').execute()

    ret += [x['name'] for x in json['items']]

    while 'nextPageToken' in json:
        json = gcs.objects().list(bucket=bucket, projection='noAcl', pageToken=json['nextPageToken']).execute()

        ret += [x['name'] for x in json['items']]

    return ret


def get(gcs, file_name, bucket=DEFAULT_BUCKET, chunk_size=KB_4):
    """
    Reads a file from Google Cloud Storage
    :param gcs: handle to the Google Cloud Storage service
    :param file_name: the file to get
    :param bucket: the name of the bucket
    :param chunk_size: the size of the chunks to upload
    :return: an array containing the bytes of the file
    """
    req = gcs.objects().get_media(bucket=bucket, object=str(file_name))
    buff = BytesIO()
    downloader = http.MediaIoBaseDownload(buff, req, chunksize=chunk_size)

    done = False
    retry_count = 0
    while not done:
        try:
            progress, done = downloader.next_chunk()
            print "Progress: %d%%\tDone: %s" % (int(progress.progress()*100), str(done))
        except errors.HttpError as err:
            print err
            if err.resp.status < 500:
                raise
        except RETRYABLE_ERRORS as err:
            print err
            retry_count += 1

            if retry_count > MAX_RETRIES:
                print "Too many failures"
                raise

    return buff.getvalue()


def put(gcs, file_name, file_contents, bucket=DEFAULT_BUCKET, chunk_size=KB_4):
    """
    Creates or updates a file in Google Cloud Storage
    :param gcs: handle to the Google Cloud Storage service
    :param file_name: the name of the file to create
    :param file_contents: the contents of the file
    :param bucket: the name of the bucket
    :param chunk_size: the size of the chunks to upload
    """

    buff = BytesIO(file_contents)
    upload = http.MediaIoBaseUpload(buff, mimetype='binary/octet-stream', chunksize=chunk_size, resumable=True)
    req = gcs.objects().insert(bucket=bucket, name=file_name, media_body=upload)

    done = False
    retry_count = 0
    while not done:
        try:
            progress, done = req.next_chunk()
            if progress:
                print "Progress: %d%%" % (int(progress.progress()*100))
        except errors.HttpError as err:
            print err
            if err.resp.status < 500:
                raise
        except RETRYABLE_ERRORS as err:
            print err
            retry_count += 1

            if retry_count > MAX_RETRIES:
                print "Too many failures"
                raise


def delete(gcs, file_name, bucket=DEFAULT_BUCKET):
    """
    Removes a file from the Google Cloud Storage
    :param gcs: handle to the Google Cloud Storage service
    :param file_name: the name of the file to delete
    :param bucket: the name of the bucket
    """
    gcs.objects().delete(bucket=bucket, object=file_name).execute()