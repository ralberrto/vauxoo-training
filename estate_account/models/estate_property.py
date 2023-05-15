from odoo import models


class EstateProperty(models.Model):
    _name = "estate.property"
    _inherit = "estate.property"

    def action_set_status_sold(self):
        return super().action_set_status_sold()
