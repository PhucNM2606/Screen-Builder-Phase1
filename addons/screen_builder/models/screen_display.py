from odoo import models, fields, api
import uuid

class ScreenDisplay(models.Model):
    _name = 'screen.builder.display'
    _description = 'Screen Builder Display Configuration'

    name = fields.Char(string="Screen Name", required=True)
    # Tự động sinh mã màn hình dạng SCR-0000X như tài liệu phân tích
    code = fields.Char(string="Screen Code", readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('screen.builder.display') or 'SCR-00000')
    
    model_id = fields.Many2one('ir.model', string="Source Model", required=True, ondelete='cascade')
    
    # Cho phép chọn Loại hiển thị theo đặc tả Phase 2
    view_type = fields.Selection([
        ('list', 'List View'),
        ('kanban', 'Kanban View'),
        ('card', 'Card View')
    ], string="Display Type", default='list', required=True)
    
    token = fields.Char(string="Security Token", readonly=True, copy=False, default=lambda self: str(uuid.uuid4()), index=True)
    public_url = fields.Char(string="Public URL", compute="_compute_public_url")
    active = fields.Boolean(default=True)

    @api.depends('token')
    def _compute_public_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.public_url = f"{base_url}/display/{record.token}"