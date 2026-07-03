import lxml.etree as ET
from odoo import http
from odoo.http import request


class ScreenBuilderController(http.Controller):

    def _parse_fields_from_arch(self, arch_db):
        """Parse <field name="..."/> from list view arch_db in exact order."""
        fields = []
        if not arch_db:
            return fields
        try:
            root = ET.fromstring(arch_db)
            # Only keep real field nodes with name attribute, preserve appearance order.
            for field_node in root.findall('.//field'):
                f_name = field_node.get('name')
                if f_name and f_name not in fields:
                    fields.append(f_name)
        except Exception:
            return []
        return fields

    def _fallback_fields(self, model_name):
        """Fallback when no list view exists: safe field types, remove system fields."""
        safe_types = {
            'char', 'text', 'integer', 'float', 'monetary', 'boolean',
            'selection', 'many2one', 'date', 'datetime'
        }
        try:
            fields_get = request.env[model_name].sudo().fields_get()
        except Exception:
            return []

        # Also exclude common technical fields
        exclude_exact = {'id', 'display_name', 'create_uid', 'create_date', 'write_uid', 'write_date', 'company_id', 'currency_id'}

        result = []

        for fname, meta in fields_get.items():
            ftype = meta.get('type')
            if fname in exclude_exact:
                continue
            if fname.startswith('ir_') or fname.startswith('access_'):
                continue
            if fname.startswith(('__',)):
                continue
            # Keep system fields out: many odoo technical fields start with x_ are business anyway, so do not drop by prefix.
            if ftype not in safe_types:
                continue
            # Avoid generic churny fields
            if fname.startswith(('message_', 'activity_')):
                continue
            result.append(fname)

        # Ensure deterministic output
        return sorted(result)

    def _resolve_view_arch(self, model_name, action, view_type):
        """Resolve the ir.ui.view arch_db for the requested view type (list or form)."""
        view = None
        view_kind = 'tree' if view_type == 'list' else 'form'

        # Prefer explicit views from action
        # Odoo action supports: view_mode, views=[(view_id, mode), ...], view_id.
        if action:
            if action.views:
                for view_id, mode in action.views:
                    if view_type == 'list' and mode in ('tree', 'list'):
                        view = request.env['ir.ui.view'].sudo().browse(view_id)
                        break
                    if view_type == 'form' and mode in ('form',):
                        view = request.env['ir.ui.view'].sudo().browse(view_id)
                        break
            if not view and getattr(action, 'view_id', False):
                view = request.env['ir.ui.view'].sudo().browse(action.view_id.id)

        # Fallback: default view of model (Odoo standard resolution)
        if not view:
            try:
                view = request.env['ir.ui.view'].sudo().search(
                    [('model', '=', model_name), ('type', '=', view_kind)],
                    order='priority asc, id desc',
                    limit=1,
                )
            except Exception:
                view = None

        if view and view.arch_db:
            return view.arch_db
        if view and view.arch_base:
            return view.arch_base
        return False

    @http.route('/display/<string:token>', type='http', auth='public', website=True)
    def render_public_screen(self, token, **kwargs):
        display = request.env['screen.builder.display'].sudo().search(
            [('token', '=', token), ('is_active', '=', True)], limit=1
        )
        if not display:
            return request.render('website.404')
        return request.render('screen_builder.public_screen_template', {'display': display})

    @http.route('/api/display/data/<string:token>', type='json', auth='public', methods=['POST'], csrf=False)
    def get_screen_data(self, token, **kwargs):
        display = request.env['screen.builder.display'].sudo().search(
            [('token', '=', token), ('is_active', '=', True)], limit=1
        )
        if not display:
            return {'error': 'Mã bảo mật Token không hợp lệ'}

        model_name = display.model_id.model
        view_type = display.view_type or 'list'

        # Action-based resolution (Odoo-compliant)
        action = display.action_id if getattr(display, 'action_id', False) else False
        arch_db = None
        if view_type in ('list', 'form'):
            arch_db = self._resolve_view_arch(model_name, action, view_type)

        fields_to_read = ['id', 'display_name']

        # If we have a list view arch, parse <field name="..."/> in order.
        if arch_db:
            parsed_fields = self._parse_fields_from_arch(arch_db)
            # Keep appearance order, but avoid duplicates and avoid system columns.
            for f in parsed_fields:
                if f not in fields_to_read:
                    fields_to_read.append(f)
        else:
            # Fallback only when model has no list view.
            # Do not use fields_get() to decide columns when list view exists.
            fallback = self._fallback_fields(model_name)
            for f in fallback[:10]:
                if f not in fields_to_read:
                    fields_to_read.append(f)

        try:
            records = request.env[model_name].sudo().search_read(
                [], fields=fields_to_read, limit=80
            )
            return {
                'screen_name': display.name,
                'view_type': view_type,
                'fields_list': fields_to_read,
                'data': records,
            }
        except Exception as e:
            return {'error': f'Lỗi hệ thống truy vấn Database: {str(e)}'}

