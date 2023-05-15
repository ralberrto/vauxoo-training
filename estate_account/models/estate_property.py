from odoo import models
from odoo.fields import Command


class EstateProperty(models.Model):
    _name = "estate.property"
    _inherit = "estate.property"

    def action_set_status_sold(self):
        for record in self:
            self.env["account.move"].create(
                {
                    "partner_id": record.buyer_id.id,
                    "move_type": "out_invoice",
                    "line_ids": [
                        Command.create(
                            {
                                "name": record.name,
                                "quantity": 1,
                                "price_unit": record.selling_price * 0.06,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Administrative fees",
                                "quantity": 1,
                                "price_unit": 100,
                            }
                        ),
                    ],
                }
            )
        return super().action_set_status_sold()
