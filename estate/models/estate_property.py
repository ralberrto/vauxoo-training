from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3), string="Available From"
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(default=True)
    status = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        copy=False,
        default="new",
        required=True,
    )
    property_type_id = fields.Many2one(comodel_name="estate.property.type")
    buyer_id = fields.Many2one("res.partner", copy=False)
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user, string="Salesman")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    _sql_constraints = [
        (
            "check_expected_price_positive",
            "CHECK (expected_price >= 0)",
            "The expected price must be strictly positive.",
        ),
        (
            "check_selling_price_positive",
            "CHECK (selling_price >= 0)",
            "The selling price must be strictly positive.",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            if prices:
                record.best_price = max(prices)
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    @api.constrains("expected_price", "selling_price")
    def _check_selling_and_expected_prices(self):
        for record in self:
            if (
                float_compare(record.selling_price, record.expected_price * 0.90, precision_rounding=2) == -1
            ) and record.selling_price != 0:
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price!"
                    "You must reduce the expected price if you want to accept this offer."
                )

    def action_set_status_canceled(self):
        for record in self:
            if record.status == "sold":
                raise UserError("Sold properties cannot be canceled.")
            record.status = "canceled"
        return True

    def action_set_status_sold(self):
        for record in self:
            if record.status == "canceled":
                raise UserError("Canceled properties cannot be sold.")
            record.status = "sold"
        return True
