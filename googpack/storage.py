import logging
import os
import sys

from google.cloud import storage


def save(bucket_name, file_name, content, storage_prefix="import-complete/"):
    try:
        # print(f"WRITING FILE: {file_name} TO BUCKET: {bucket_name}")
        storage_file = storage_prefix + file_name
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(f"{storage_file}")
        blob.upload_from_string(content, content_type="application/json")
        file_path = "gs://" + bucket_name + "/" + blob.name

        return file_path

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_msg = f"Exception processing people/update. {type(ex).__name__}, line [{exc_tb.tb_lineno}], {str(ex)}"
        print(log_msg)
        logging.error(f"Error: {log_msg}")

    return None
