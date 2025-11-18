{
    "name": "AI Partner Classification",
    "version": "19.0.1.0.0",
    "summary": "AI-based customer classification and insights",
    "author": "Accounts Techs",
    "website": "https://actechsit.com",
    "category": "Sales/CRM",
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts",
        "account",
        "crm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/res_partner_view.xml",
        "views/dashboard_view.xml",
        "views/ai_dashboard_view.xml",
        "views/menuitems.xml",
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}
