import lxml.etree as ET
from odoo import http
from odoo.http import request

class ScreenBuilderController(http.Controller):

    @http.route('/display/<string:token>', type='http', auth='public', website=True)
    def render_public_screen(self, token, **kwargs):
        display = request.env['screen.builder.display'].sudo().search([('token', '=', token), ('active', '=', True)], limit=1)
        if not display:
            return request.render('website.404')
        return request.render('screen_builder.public_screen_template', {'display': display})

    @http.route('/api/display/data/<string:token>', type='json', auth='public', methods=['POST'], csrf=False)
    def get_screen_data(self, token, **kwargs):
        display = request.env['screen.builder.display'].sudo().search([('token', '=', token), ('active', '=', True)], limit=1)
        if not display:
            return {'error': 'Mã bảo mật Token không hợp lệ'}

        model_name = display.model_id.model
        view_type = display.view_type or 'list'
        
        fields_to_read = ['id', 'display_name']
        
        # Tìm kiến trúc View XML gốc của Odoo để tự động trích xuất cột dữ liệu
        view_domain = [('model', '=', model_name), ('type', '=', 'tree' if view_type == 'list' else 'kanban')]
        ui_view = request.env['ir.ui.view'].sudo().search(view_domain, order='priority asc, id desc', limit=1)
        
        if ui_view and ui_view.arch_base:
            try:
                root = ET.fromstring(ui_view.arch_base)
                for field_node in root.findall('.//field'):
                    f_name = field_node.get('name')
                    if f_name and f_name not in fields_to_read:
                        fields_to_read.append(f_name)
            except Exception:
                pass

        # Trường hợp dự phòng nếu Model chưa có view hoặc phân tích XML thất bại
        if len(fields_to_read) <= 2:
            try:
                fields_get = request.env[model_name].fields_get()
                fields_to_read += [k for k, v in fields_get.items() if v.get('type') in ['char', 'selection', 'integer']][:4]
            except Exception:
                pass

        try:
            # Truy vấn lấy dữ liệu thực tế từ database theo danh sách cột động
            records = request.env[model_name].sudo().search_read([], fields=fields_to_read, limit=80)
            return {
                'screen_name': display.name,
                'view_type': view_type,
                'fields_list': fields_to_read,
                'data': records
            }
        except Exception as e:
            return {'error': f'Lỗi hệ thống truy vấn Database: {str(e)}'}