import json
import logging
import os
import sys

import arrow
from google.cloud import secretmanager


def check_key(key_file_name="sa", secret_name=""):
    """Description
    Pulls the service account key from Secrets Manager and writes a local key.
    The local key is checked for age and requeries for a fresh (rotated) key.

    If the key file either does not exist, or is older than key the
    time-to-live (ttl) period then refresh the key from the secrets
    manager and write the new key to file.

    Args
        key_file_name:  service account key file name w/o '.json'
        secret_name:    secret name for retreiving updated service account key
    """
    # LOCAL_WRITE_DIR = "/tmp/"
    LOCAL_WRITE_DIR = ""

    key_ttl = 10  # minutes
    if ".json" not in key_file_name:
        key_file_name = f"{key_file_name}.json"
    do_key_refresh = False
    refresh_reason = ""

    try:
        file_path = os.path.join(os.getcwd(), LOCAL_WRITE_DIR, key_file_name)
        if not os.path.exists(file_path):
            do_key_refresh = True
            refresh_reason = "The credentials key does not exist"
        elif do_key_refresh is False:
            credentials_file_timestamp = os.path.getmtime(file_path)
            created_time = arrow.get(credentials_file_timestamp)
            if created_time.shift(minutes=key_ttl) < arrow.utcnow():
                refresh_reason = f"""The credentials key found exceeds TTL
                                (minutes={key_ttl})"""
                do_key_refresh = True
        if do_key_refresh:
            # get key from secret manager
            secret_value = get_secret(secret_name)
            key = json.loads(secret_value)
            logging.info(
                f"{refresh_reason}. Writing new credentials file to {file_path}."
            )
            with open(file_path, "w") as file:
                file.write(json.dumps(key))
        return file_path
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_msg = f"Exception retreiving secret. {type(ex).__name__}, line [{exc_tb.tb_lineno}], {str(ex)}"
        logging.error(f"{log_msg}")
        return None


def get_secret(secret_name):
    try:
        secrets_client = secretmanager.SecretManagerServiceClient()
        # logging.info(f'accessing secret at path: {secret_name}')
        response = secrets_client.access_secret_version(request={"name": secret_name})
        # logging.debug(f"Secret retrieval success [{ name }]", exc_info=True)
        return response.payload.data.decode("UTF-8")
    except PermissionError as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_msg = f"Exception authenticating for secret. {type(ex).__name__}, line [{exc_tb.tb_lineno}], {str(ex)}"
        logging.error(f"{log_msg}")
        raise
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_msg = f"Exception retreiving secret. {type(ex).__name__}, line [{exc_tb.tb_lineno}], {str(ex)}"
        logging.error(f"{log_msg}")
        print(log_msg)
        raise
