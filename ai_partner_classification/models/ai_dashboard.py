from odoo import api, fields, models


class AiPartnerDashboard(models.TransientModel):
    _name = "ai.partner_dashboard"
    _description = "AI Partner Dashboard"

    total_customers = fields.Integer(string="Total AI Customers", readonly=True)
    vip_customers = fields.Integer(string="VIP Customers", readonly=True)
    high_value_customers = fields.Integer(string="High Value Customers", readonly=True)
    high_risk_customers = fields.Integer(string="High Risk Customers", readonly=True)
    inactive_customers = fields.Integer(string="Inactive Customers", readonly=True)
    low_value_customers = fields.Integer(string="Low Value Customers", readonly=True)

    @api.model
    def default_get(self, fields_list):
        """نحسب المؤشرات في كل مرة نفتح فيها الداشبورد."""
        res = super().default_get(fields_list)

        Partner = self.env["res.partner"].sudo()
        base_domain = [("x_ai_classification", "!=", False)]

        res["total_customers"] = Partner.search_count(base_domain)
        res["vip_customers"] = Partner.search_count(
            base_domain + [("x_ai_classification", "=", "vip")]
        )
        res["high_value_customers"] = Partner.search_count(
            base_domain + [("x_ai_classification", "=", "high_value")]
        )
        res["high_risk_customers"] = Partner.search_count(
            base_domain + [("x_ai_classification", "=", "high_risk")]
        )
        res["inactive_customers"] = Partner.search_count(
            base_domain + [("x_ai_classification", "=", "inactive")]
        )
        res["low_value_customers"] = Partner.search_count(
            base_domain + [("x_ai_classification", "=", "low_value")]
        )

        return res
