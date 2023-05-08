from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", string="Deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    _sql_constraints = [
        ("check_offer_price_positive", "CHECK (price > 0)", "The price offered must be greater than 0."),
    ]

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            if not record.create_date:
                create_date = fields.Date.today()
            else:
                create_date = record.create_date.date()
            record.date_deadline = fields.Date.add(create_date, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days

    def action_set_status_accepted(self):
        for record in self:
            if "accepted" in record.property_id.offer_ids.mapped("status"):
                raise UserError("Only one offer may be accepted.")
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price

    def action_set_status_refused(self):
        self.write({"status": "refused"})
        self.property_id.write({"selling_price": 0, "buyer_id": False})
