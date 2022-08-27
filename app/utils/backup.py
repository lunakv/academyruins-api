import hashlib
import logging
import os.path
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from app.resources import static_paths as paths
from app.utils import notifier

load_dotenv()


class Backup:
    """
    Handles backup of raw files from a directory to an S3-like bucket
    """

    def __init__(self, endpoint, key_id, application_key, bucket_name):
        self.b2 = boto3.resource(
            service_name="s3",
            endpoint_url=endpoint,
            aws_access_key_id=key_id,
            aws_secret_access_key=application_key,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = bucket_name

    def get_objects(self, directory):
        response = self.b2.Bucket(self.bucket).objects.filter(Prefix=directory + "/")
        return_dict = {}
        for obj in response:
            return_dict[obj.key] = obj
        return return_dict

    def is_current_object(self, file_path, file_key, objects):
        if file_key not in objects:
            return False

        with open(file_path, "rb") as fd:
            to_sum = fd.read()
        digest = hashlib.md5(to_sum).hexdigest()
        object_tag = objects[file_key].e_tag[1:-1]  # e_tag includes quotation marks around the value
        return object_tag == digest

    def sync_directory(self, basedir, directory):
        dir_path = os.path.join(basedir, directory)
        objects = self.get_objects(directory)

        for file_name in os.listdir(dir_path):
            file_key = directory + "/" + file_name
            file_path = os.path.join(dir_path, file_name)
            if self.is_current_object(file_path, file_key, objects):
                logging.debug("file current: " + file_key)
            else:
                self.upload_file(file_path, file_key)

    def upload_file(self, file_path, file_key):
        self.b2.Bucket(self.bucket).upload_file(file_path, file_key)
        logging.debug("uploaded file: " + file_key)


def run_backup():
    key_id = os.getenv("BACKUP_KEY_ID")
    if not key_id:
        return
    app_key = os.getenv("BACKUP_APP_KEY")
    endpoint = os.getenv("BACKUP_ENDPOINT")
    bucket = os.getenv("BACKUP_BUCKET_NAME")
    b2 = Backup(endpoint, key_id, app_key, bucket)
    for directory in ["cr", "mtr", "ipg"]:
        try:
            b2.sync_directory(paths.docs_dir, directory)
            logging.info("Backup completed for directory " + directory)
        except ClientError as ce:
            logging.error("Error while syncing backup for directory " + directory)
            logging.error(ce)
            notifier.notify("ClientError when syncing directory " + directory, title="Backup Error")
