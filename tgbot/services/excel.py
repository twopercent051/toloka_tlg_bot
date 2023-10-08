from datetime import timedelta

from openpyxl import Workbook
from openpyxl.styles import Font
import os


class ExcelCreate:

    @classmethod
    def create_users(cls, users: list):
        file_path = f"{os.getcwd()}/all_users.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append(
            (
                "USER_ID",
                "USERNAME",
                "Дата регистрации (МСК)",
            )
        )
        ft = Font(bold=True)
        for row in ws['A1:T1']:
            for cell in row:
                cell.font = ft

        for user in users:
            create_datetime = (user["reg_dtime"] + timedelta(hours=3)).strftime("%d-%m-%Y %H:%M")
            ws.append(
                (
                    user["user_id"],
                    user["username"],
                    create_datetime,
                )
            )
        wb.save(filename=file_path)
        return file_path
