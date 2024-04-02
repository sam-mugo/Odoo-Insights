# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
import datetime
from odoo.http import request


class AccountMove(models.Model):
    _inherit = 'account.move'

    # retrieves the customer paid and unpaid Invoices
    @api.model
    def get_paid_customer_invoices(self):
        # todo : add date as parameter and domain
        result = self.sudo().read_group(
            [('move_type', '=', 'out_invoice'), ("state", "=", "posted"), ("payment_state", "=", "paid")],
            fields={"amount_total_signed:sum"}, groupby={"state", "payment_state", "move_type"})
        return result

    # retrieves unpaid customer invoices
    @api.model
    def get_unpaid_customer_invoices(self):
        # todo : add date as parameter and domain
        result = self.env['account.move'].read_group(
            [('move_type', '=', 'out_invoice'), ("state", "=", "posted"),
             ('payment_state', 'in', ['partial', 'not_paid'])],
            fields={"amount_total_signed:sum"}, groupby={"state", "payment_state", "move_type"})
        return result
    
    # retrieves the vendor paid  Invoices
    @api.model
    def get_paid_vendor_invoices(self):
        # todo : add date as parameter and domain
        result = self.env['account.move'].sudo().search_read(
            [('move_type', '=', 'in_invoice'), ("state", "=", "posted"), ("payment_state", "=", "paid")],
            fields=["amount_total_signed"])
        return result
    
    # retrieves the vendors unpaid invoices
    @api.model
    def get_unpaid_vendor_invoices(self):
        # todo : add date as parameter and domain
        result = self.env['account.move'].search_read(
            [('move_type', '=', 'in_invoice'), ("state", "=", "posted"),
             ('payment_state', 'in', ['partial', 'not_paid'])],
            fields=["amount_total_signed", "partner_id", "invoice_date_due"])
        return result

    # retrieves the aged receivables
    @api.model
    def get_aged_receivable(self):
        result = self.sudo().search_read(
            [('state', '=', 'posted'),
             ('move_type', 'not in', ['in_invoice', 'in_refund', 'in_receipt']),
             ('payment_state', 'in', ['partial', 'not_paid'])],
            fields=["amount_total_signed", "partner_id", "invoice_date_due"], order='invoice_date_due desc')
        return result

    # This function is to make sure we get the user's correct company ID API passes false company_id
    def get_current_company_value(self):
        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]

        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids

    # gets the total profits in month,year,week depending on the passed parameter date
    @api.model
    def get_profit_income(self, date):
        company_id = self.get_current_company_value()
        states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select account_move_line.id from  account_account, account_move_line where 
                                            account_move_line.account_id = account_account.id AND
                                            %s AND
                                           (account_account.internal_group = 'income' or    
                                           account_account.internal_group = 'expense' )                                       
                                           AND Extract(%s FROM account_move_line.date) = Extract(%s FROM DATE(NOW()))  
                                           AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''           
                                            ''') % (states_arg, date, date))
        profit = [row[0] for row in self._cr.fetchall()]
        return profit

    # returns the IDs of the unreconciled move lines
    @api.model
    def get_unreconciled_items(self):
        self._cr.execute('''
                                SELECT l.id
                                FROM account_move_line l
                                JOIN account_account a ON l.account_id = a.id
                                WHERE l.full_reconcile_id IS NULL
                                    AND l.balance != 0
                                    AND a.reconcile IS TRUE
                                GROUP BY l.id;
 ''')
        record = [row[0] for row in self._cr.fetchall()]
        return record

