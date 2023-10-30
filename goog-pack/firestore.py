import json
import logging
import os
from pprint import pprint

# import arrow
from google.cloud import firestore


def get_config(config_env):
    try:
        client = firestore.Client()

        doc = client.collection("configs").document(config_env.lower()).get()
        logging.info(f"Retrieved config: {config_env.lower()}")
        return doc.to_dict()
    except Exception as ex:
        logging.error(f"Error: {ex}")

    return None
