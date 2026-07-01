from odoo import http
from odoo.http import request


class DisplayController(http.Controller):

    @http.route("/display/<string:token>", auth="public", type="http")
    def display_page(self, token, **kw):

        display = request.env["screen.builder.display"].sudo().search([
            ("token", "=", token)
        ], limit=1)

        if not display:
            return request.not_found()

        return request.render(
            "screen_builder.display_page",
            {"token": token}
        )


    @http.route("/display/api/<string:token>", auth="public", type="http")
    def display_api(self, token, **kw):

        display = request.env["screen.builder.display"].sudo().search([
            ("token", "=", token)
        ], limit=1)

        if not display:
            return request.not_found()

        record = display.get_record()

        return request.make_response(
            request.json_response({
                "display": {
                    "name": display.name,
                    "model": display.model_id.model,
                },
                "record": {
                    "id": record.id,
                    "name": record.display_name if record else "",
                }
            })
        )