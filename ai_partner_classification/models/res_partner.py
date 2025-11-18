from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # حقل التصنيف الذكي
    x_ai_classification = fields.Selection(
        selection=[
            ("vip", "VIP"),
            ("high_value", "High Value"),
            ("active", "Active"),
            ("low_value", "Low Value"),
            ("high_risk", "High Risk"),
            ("inactive", "Inactive"),
        ],
        string="AI Classification",
        default="active",
        tracking=True,
    )

    # ====== زر يدوي من الفورم ======
    def action_recalculate_ai_classification(self):
        """إعادة حساب تصنيف الذكاء لهذا العميل/العملاء فقط."""
        self._compute_ai_classification_batch()
        return True

    # ====== كرون يعيد تصنيف كل العملاء ======
    @api.model
    def cron_recalculate_ai_classification(self):
        partners = self.search([])
        partners._compute_ai_classification_batch()
        return True

    # ====== حساب التصنيف لمجموعة ======
    def _compute_ai_classification_batch(self):
        today = fields.Date.context_today(self)
        for partner in self:
            metrics = partner._get_ai_metrics(today)
            classification = partner._get_classification_from_metrics(metrics)
            partner.x_ai_classification = classification

    # ====== استخراج المقاييس المالية ======
    def _get_ai_metrics(self, today):
        self.ensure_one()

        invoices = self.invoice_ids.filtered(
            lambda m: m.move_type in ("out_invoice", "out_refund")
            and m.state == "posted"
        )

        invoice_count = len(invoices)

        if invoice_count:
            total_amount = sum(invoices.mapped("amount_total_signed"))
            avg_amount = total_amount / invoice_count
        else:
            total_amount = 0.0
            avg_amount = 0.0

        overdue_invoices = invoices.filtered(
            lambda m: m.invoice_date_due
            and m.invoice_date_due < today
            and m.payment_state in ("not_paid", "partial")
        )
        overdue_ratio = (
            (len(overdue_invoices) / invoice_count) * 100.0 if invoice_count else 0.0
        )

        return {
            "invoice_count": invoice_count,
            "total_amount": total_amount,
            "avg_amount": avg_amount,
            "overdue_ratio": overdue_ratio,
        }

    # ====== منطق التصنيف ======
    def _get_classification_from_metrics(self, metrics):
        invoice_count = metrics["invoice_count"]
        total_amount = metrics["total_amount"]
        avg_amount = metrics["avg_amount"]
        overdue_ratio = metrics["overdue_ratio"]

        # ما عنده ولا فاتورة → Inactive
        if invoice_count == 0:
            return "inactive"

        # VIP: مجموع فواتير عالي + متوسط فاتورة عالي + تأخير قليل
        if total_amount >= 20000 and avg_amount >= 5000 and overdue_ratio < 30:
            return "vip"

        # High Value: صرف جيد وتأخير معقول
        if total_amount >= 5000 and overdue_ratio < 50:
            return "high_value"

        # High Risk: نسبة تأخير عالية
        if overdue_ratio >= 50:
            return "high_risk"

        # Low Value: تعامل بسيط جداً
        if total_amount < 1000:
            return "low_value"

        # الباقي Active
        return "active"
