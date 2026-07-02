from odoo import models, fields, api
import uuid

class ScreenDisplay(models.Model):
    _name = 'screen.builder.display'
    _description = 'Screen Builder Display Configuration'

    name = fields.Char(string="Screen Name", required=True)
    # Tự động sinh mã màn hình dạng SCR-0000X như tài liệu phân tích
    code = fields.Char(
        string="Screen Code",
        readonly=True,
        copy=False,
        default="",
    )
    
    model_id = fields.Many2one('ir.model', string="Source Model", required=True, ondelete='cascade')
    
    # Cho phép chọn Loại hiển thị theo đặc tả Phase 2
    view_type = fields.Selection([
        ('list', 'List View'),
        ('form', 'Form View'),
        ('kanban', 'Kanban View'),
        ('card', 'Card View')
    ], string="Display Type", default='list', required=True)

    # Người dùng chọn action/menu (ir.actions.act_window) để Odoo resolve đúng list view tree
    action_id = fields.Many2one(
        'ir.actions.act_window',
        string='Source Action',
        ondelete='set null',
        help='Select an act_window so Odoo can resolve the exact List (Tree) view arch_db used by the action.'
    )

    
    token = fields.Char(string="Security Token", readonly=True, copy=False, default=lambda self: str(uuid.uuid4()), index=True)
    public_url = fields.Char(string="Public URL", compute="_compute_public_url")
    is_active = fields.Boolean(string="Active", default=True)

    @api.depends('token')
    def _compute_public_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.public_url = f"{base_url}/display/{record.token}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "screen.builder.display"
                )
        return super().create(vals_list)