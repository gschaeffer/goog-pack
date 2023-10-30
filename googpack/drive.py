import os

# from flask import current_app as app
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


# DRIVE_FOLDER_ID = app.config.get("DRIVE_FOLDER_ID")


def main():
    upload()
    list()


def list(folder_id):
    file_list = drive.ListFile(
        {"q": "'{}' in parents and trashed=false".format(folder_id)}
    ).GetList()
    for file in file_list:
        print("title: %s, id: %s" % (file["title"], file["id"]))


def upload(file_path, file_title, folder_id):
    try:
        GoogleAuth.DEFAULT_SETTINGS["client_config_file"] = os.path.join(
            os.getcwd(), "api", "client_secrets.json"
        )
        gfile = drive.CreateFile({"parents": [{"id": folder_id}]})
        gfile["title"] = file_title
        gfile.SetContentFile(file_path)
        gfile.Upload()
        print(
            "Certificate PDF uploaded to Drive. Title: %s, ID: %s"
            % (gfile.get("title", "no-title"), gfile.get("id", "no-id"))
        )
        return gfile.get("id")
    except Exception as ex:
        payload = {
            "local_file": file_path,
            "destination_file": file_title,
            "drive_folder_id": folder_id,
        }
        print(
            f"Error on Drive upload. Details: {payload}; Error type: {type(ex)}; Error: {str(ex)}"
        )
        return None


if __name__ == "__main__":
    main()
