from odoo import fields, models


class GenerateDisplayWizard(models.TransientModel):
    _name = "generate.display.wizard"
    _description = "Generate Display Wizard"

    display_url = fields.Char(readonly=True)

    def action_generate(self):
        self.ensure_one()

        model_name = self.env.context.get("active_model")
        record_id = self.env.context.get("active_id")

        if not model_name:
            raise ValueError("Missing active_model")
        if not record_id:
            raise ValueError("Missing active_id")

        model = self.env["ir.model"].search(
            [("model", "=", model_name)],
            limit=1,
        )
        if not model:
            raise ValueError(f"Model not found: {model_name}")

        # Người dùng chọn Menu/Action (act_window) khi tạo Display.
        # Trong Odoo, wizard thường nhận action_id qua context.
        action_id = self.env.context.get("default_action_id") or self.env.context.get("action_id")
        action = self.env["ir.actions.act_window"].sudo().browse(action_id) if action_id else False
        if action and action.exists():
            action = action.sudo()
        else:
            action = False

        display = self.env["screen.builder.display"].create({
            "name": f"{model_name}-{record_id}",
            "model_id": model.id,
            "record_id": record_id,
            "action_id": action.id if action else False,
        })

        self.display_url = display.public_url

        return {
            "type": "ir.actions.act_window",
            "res_model": "generate.display.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

