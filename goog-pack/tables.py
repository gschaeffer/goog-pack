import json
import os
import sys

from google.area120 import tables_v1alpha1
from google.oauth2 import service_account


class TablesBase:
    """
    TablesBase class provides programmatic access to Tables API.

    Args:
        **kwargs: dictionary with required configuration values.
            tbl_mbrs:       Members table name
            tbl_achs:       Achievements table name
            svc_key_path:   Path to service account key for authentication
            term_status:    Status to be used for departed employees

    Returns:
        Instance of Tables class.

    Raises:
        KeyError: Raises an exception.
    """

    _client = None
    __slots__ = [
        "tbl_mbrs",
        "tbl_achs",
        "svc_key_path",
        "term_status",
    ]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_row(self, table_id: str, data: dict):
        row = tables_v1alpha1.Row(ignore_unknown_fields=True)
        row.values = data
        request = tables_v1alpha1.CreateRowRequest(parent=f"tables/{table_id}", row=row)
        row = self._get_client().create_row(request=request)

        # row name format = tables/TABLE_ID/rows/ROW_ID
        return row.name

    def delete_row(self, name: str):
        try:
            request = tables_v1alpha1.DeleteRowRequest(name=name)
            response = self._get_client().delete_row(request=request)
            return response
        except Exception as ex:
            print(f"error: {ex}")

    def _get_client(self):
        if self._client == None:
            # svc_key = os.path.join(os.getcwd(), self.svc_key_name)
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = service_account.Credentials.from_service_account_file(
                self.svc_key_path, scopes=scopes
            )

            client = tables_v1alpha1.TablesServiceClient(credentials=creds)
        return client

    def _get_lookup_id(self, table_id: str, filter: str):
        r = self.get_rows(table_id, filter)
        if r is None:
            return
        else:
            for idx, k in enumerate(r):
                return k
        return None

    def get_row(
        self,
        table_id: str,
        row_id: str,
    ):
        request = tables_v1alpha1.GetRowRequest(
            name=f"tables/{table_id}/rows/{row_id}",
        )
        return self._get_client().get_row(request=request)

        return name.split("/")[-1]

    def get_row_by_id(
        self,
        client: tables_v1alpha1.TablesServiceAsyncClient,
        table_id: str,
        row_id: str,
    ):
        if "rows/" in row_id:
            row_id = self.get_row_id_from_name(row_id)

        request = tables_v1alpha1.GetRowRequest(
            name=f"tables/{table_id}/rows/{row_id}",
        )
        return client.get_row(request=request)

    def get_row_id_from_row(self, name: str):
        if "rows/" in name:
            return name.split("/")[-1]
        return name

    def get_rows(
        self,
        table_id: str,
        filter: str,
    ):
        # print(f"table: {table_id}, filter: {filter}")
        request = tables_v1alpha1.ListRowsRequest(
            parent=f"tables/{table_id}", filter=filter
        )
        client = self._get_client()
        result = client.list_rows(request=request)
        rows = []
        for r in result:
            rows.append(r.name)
        return rows

    def update_row(self, row: dict):
        try:
            update_request = tables_v1alpha1.UpdateRowRequest(row=row)
            response = self._get_client().update_row(request=update_request)
            return response
        except Exception as ex:
            print(f"error: {ex}")


class Tables(TablesBase):
    """
    Tables class provides programmatic access to Tables data storage.

    Args:
        **kwargs: dictionary with required configuration values.
            tbl_mbrs:       Members table name
            tbl_achs:       Achievements table name
            svc_key_path:   Path to service account key for authentication
            term_status:    Status to be used for departed employees

    Returns:
        Instane of Tables class.

    Raises:
        KeyError: Raises an exception.

    Example:
        config = {
            "tbl_mbrs": "members",
            "tbl_achs": "achievements",
            "svc_key_path": os.path.join(os.getcwd(), "sa.json"),
            "term_status": "Departed",
        }
        t = tables.Tables(**config)
        print(t.tbl_rg)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_member(self, data):
        """
        data = {
            "Member": "email",
            "Manager": "email",
            "Department": "department",
            "Region": "region",
            "Territory": "territory",
            "Pod": "pod",
        }
        """
        try:
            required_fields = {"Member"}
            allowed_fields = required_fields | {
                "Manager",
                "Department",
                "Region",
                "Territory",
                "Pod",
            }

            if required_fields <= data.keys() <= allowed_fields:
                return super().add_row(super().tbl_mbrs, data)
            else:
                raise KeyError(
                    f"Required key values are: {required_fields}. Optional fields are: {allowed_fields}"
                )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_msg = f"Exception adding emp. {type(ex).__name__}, line [{exc_tb.tb_lineno}], {str(ex)}"
            print(log_msg)
            return False

    def delete_member(self, row: str):
        return super().delete_row(row)

    def get_achievement(self, row: str):
        return super().get_row(super().tbl_achs, self.get_row_id_from_row(row))

    def get_achievements(self, user_email: str):
        return super().get_rows(super().tbl_achs, f'values.Member="{user_email}"')

    def get_member(self, row: str):
        return super().get_row(super().tbl_mbrs, self.get_row_id_from_row(row))

    def get_members(self, user_email: str):
        return super().get_rows(super().tbl_mbrs, f'values.Member="{user_email}"')

    def update_achievement(self, row: str):
        return super().update_row(row)

    def update_member(self, row: dict):
        return super().update_row(row)

    def update_member_contact(self, row: dict, group_contact: str):
        # get rid of any doit-intl.com fk lookups by first saving to null
        if "intl.com" in row.values["Group Contact"]:
            del row.values["Group Contact"]
            updated_row = super().update_row(row)

        fk = super()._get_lookup_id(
            super().tbl_mbrs, f'values.Contact="{group_contact}"'
        )

        if fk:
            row.values["reporting-group-members"] = fk
        if fk is None:
            if "intl" in group_contact:
                group_contact = group_contact.split("@")[0] + "@doit.com"
            else:
                group_contact = group_contact.split("@")[0] + "@doit-intl.com"
            fk = super()._get_lookup_id(
                super().tbl_rg, f'values.Contact="{group_contact}"'
            )

        if fk:
            row.values["reporting-group-members"] = fk
            return super().update_row(row)
        return None

    def terminate_achievement(self, row: str):
        ach = self.get_achievement(row)
        ach.values["Status"] = self.term_status
        return super().update_row(ach)
