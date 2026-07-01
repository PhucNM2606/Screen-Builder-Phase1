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

        model = self.env["ir.model"].search(
            [("model", "=", model_name)],
            limit=1,
        )

        if not model:
            raise ValueError(f"Model not found: {model_name}")

        view = self.env["ir.ui.view"].search(
            [
                ("model", "=", model_name),
                ("type", "=", "form"),
            ],
            limit=1,
        )

        display = self.env["screen.builder.display"].create({
            "name": f"{model_name}-{record_id}",
            "model_id": model.id,
            "record_id": record_id,
            "view_id": view.id if view else False,
        })

        self.display_url = display.public_url

        return {
            "type": "ir.actions.act_window",
            "res_model": "generate.display.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }