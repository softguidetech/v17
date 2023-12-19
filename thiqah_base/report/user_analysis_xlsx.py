# -*- coding: utf-8 -*-

"""
Support: https://xlsxwriter.readthedocs.io/tutorial01.html
"""

from odoo import models, fields, _, api
#['row', 'user', 'login_date', 'redirect_to']
# ['row', 'user_id', 'create_date', 'category_type', 'method']

MAPPING_ = {
    'row': 'Row',
    'user': 'User',
    'user_id': 'User',
    'login_date': 'Login Date',
    'redirect_to': 'Redirect To',
    'create_date': 'Create Date',
    'category_type': 'Department',
    'method': 'Action',
}

FONT_COLOR = '#444b82'


class userAnalysisXlsx(models.AbstractModel):
    _name = 'report.thiqah_base.user_analysis_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _header_formatting(self, header):
        """
        Inplace Approach.
        """
        for counter in range(len(header)):
            header_item = MAPPING_.get(header[counter], False)
            if header_item:
                header[counter] = header_item
        return header

    def generate_xlsx_report(self, workbook, data, user_analysis):
        # Create a workbook and add a worksheet.
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'bold': True, 'font_color': FONT_COLOR, 'font_size': 16})
        cell_format.set_center_across()
        worksheet.set_column('A:A', 25, cell_format)
        worksheet.set_column('B:C', 25, cell_format)
        worksheet.set_column('D:D', 25, cell_format)
        worksheet.set_column('D:D', 25, cell_format)
        worksheet.set_column('E:E', 25, cell_format)

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # gathering data
        user_analysis_data = data['user_analysis_data']['get_data']

        if user_analysis_data:
            # analysis_type = data['user_analysis_data']['analysis_type']

            # data we want to write to the worksheet(final_data)
            header = list(user_analysis_data[0].keys())
            header = self._header_formatting(header)
            final_data = [header]

            # extract data
            for user_analysis_data_ in user_analysis_data:
                final_data.append([i for i in user_analysis_data_.values()])

            header_length = len(header)

            for final_data_ in final_data:
                for index in range(header_length):
                    worksheet.write(
                        row, col+index, final_data_[index], cell_format)
                row += 1

            # if analysis_type == 'login':
            #     # Iterate over the data and write it out row by row.
            #     #['row', 'user', 'login_date', 'redirect_to']
            #     for item in final_data:
            #         worksheet.write(row, col,     item[0], cell_format)
            #         worksheet.write(row, col + 1, item[1], cell_format)
            #         worksheet.write(row, col + 2, item[2], cell_format)
            #         worksheet.write(row, col + 3, item[3], cell_format)
            #         row += 1

            # if analysis_type == 'request':
            #     # Iterate over the data and write it out row by row.
            #     # ['row', 'user_id', 'create_date', 'category_type', 'method']
            #     for item in final_data:
            #         worksheet.write(row, col,     item[0], cell_format)
            #         worksheet.write(row, col + 1, item[1], cell_format)
            #         worksheet.write(row, col + 2, item[2], cell_format)
            #         worksheet.write(row, col + 3, item[3], cell_format)
            #         worksheet.write(row, col + 4, item[4], cell_format)
            #         row += 1
