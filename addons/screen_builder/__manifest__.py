{
    "name": "Screen Builder",
    "version": "1.0",
    "category": "Tools",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/screen_display_views.xml",
        "views/display_templates.xml",
        "wizard/generate_display_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "screen_builder/static/src/js/display.js",
        ],
    },
    "installable": True,
    "application": True,
}