# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):

    _inherit = "ir.http"

    def session_info(self):
        result = super(IrHttp, self).session_info()
        company = request.session.uid and request.env.user.company_id
        company_title = company and company.company_title or "THIQAH"
        result["user_companies"]["allowed_companies"][company.id].update({
            "company_title":company_title
        })
        return result
