from odoo import api, fields, models
import uuid


class ScreenDisplay(models.Model):
    _name = "screen.builder.display"
    _description = "Public Display"

    name = fields.Char(required=True)

    token = fields.Char(
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
        index=True,
    )

    model_id = fields.Many2one(
        "ir.model",
        required=True,
        ondelete="cascade",   
    )

    record_id = fields.Integer(required=True)

    view_id = fields.Many2one(
        "ir.ui.view",
        required=True,
        ondelete="cascade",
    )

    active = fields.Boolean(default=True)

    expire_date = fields.Datetime()

    public_url = fields.Char(
        compute="_compute_public_url",
        store=False,
    )

    @api.depends("token")
    def _compute_public_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        for rec in self:
            rec.public_url = f"{base}/display/{rec.token}"

    # helper
    def get_record(self):
        self.ensure_one()
        if not self.model_id:
            return self.env[self.model_id.model].browse()

        return self.env[self.model_id.model].sudo().browse(self.record_id)