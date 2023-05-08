from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        (
            "name_unique",
            "UNIQUE (name)",
            "A property tag with the same name already exists.",
        ),
    ]
