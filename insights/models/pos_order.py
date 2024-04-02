# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
import datetime
import calendar


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # gets the out-of-stock products
    @api.model
    def get_out_of_stock(self):
        result = self.env['stock.warehouse.orderpoint'].search_read(
            [('qty_on_hand', '<=', 0), ("product_id.available_in_pos", "=", True)],
            fields=["product_id", "qty_on_hand", "qty_forecast"])
        result = sorted(result, key=lambda x: x["qty_on_hand"])
        return result

    # gets the top paying customers
    @api.model
    def get_top_customers(self):
        result = self.env['res.partner'].search_read([], fields=["name", "total_invoiced"])
        result = sorted(result, key=lambda x: x["total_invoiced"], reverse=True)[:5]
        return result

    # gets the pos orders
    @api.model
    def get_all(self):
        return self.search_read(fields=["name", "session_id", "date_order", "pos_reference", "amount_total"])

    # gets all orders done this week and maps them to 7 entry dict
    @api.model
    def get_all_week(self):
        date_week = fields.Date.today() - relativedelta(days=7)
        domain = [('date_order', '>', date_week)]
        result = []
        data = self.with_context(lang="en").read_group(domain=domain,
                                                       fields=['amount_total:sum'], groupby=['date_order:day'],
                                                       orderby='date_order asc')

        if not data:
            return []
        else:
            for i in range(7):
                weekday = datetime.datetime.strftime(
                    datetime.datetime.strptime(data[0]["date_order:day"], "%d %b %Y") + datetime.timedelta(days=i), "%A")
                found = False
                for entry in data:
                    if entry["date_order:day"] == datetime.datetime.strftime(
                            datetime.datetime.strptime(data[0]["date_order:day"], "%d %b %Y") + datetime.timedelta(days=i),
                            "%d %b %Y"):
                        result.append({'day': weekday, 'data': entry})
                        found = True
                        break
                if not found:
                    result.append({'day': weekday, 'data': {'date_order_count': 0, 'amount_total': 0}})
        return result

    # gets all orders done this month and maps them to 30 entry dict
    @api.model
    def get_all_month(self):
        date_week = fields.Date.today() - relativedelta(days=30)
        domain = [('date_order', '>', date_week)]
        result = []
        data = self.with_context(lang="en").read_group(domain=domain,
                               fields=['amount_total:sum'], groupby=['date_order:day'],
                               orderby='date_order asc')
        if not data:
            return []
        else:
            for i in range(30):
                weekday = datetime.datetime.strftime(
                    datetime.datetime.strptime(data[0]["date_order:day"], "%d %b %Y") + datetime.timedelta(days=i),
                    "%d")
                found = False
                for entry in data:
                    if entry["date_order:day"] == datetime.datetime.strftime(
                            datetime.datetime.strptime(data[0]["date_order:day"], "%d %b %Y") + datetime.timedelta(
                                days=i),
                            "%d %b %Y"):
                        result.append({'day': weekday, 'data': entry})
                        found = True
                        break
                if not found:
                    result.append({'day': weekday, 'data': {'date_order_count': 0, 'amount_total': 0}})
        return result

    # gets all orders done this year and maps them to 12 entry dict
    @api.model
    def get_all_year(self):
        date_week = fields.Date.today() - relativedelta(days=365)
        domain = [('date_order', '>', date_week)]
        result = []
        data = self.with_context(lang="en").read_group(domain=domain,
                               fields=['amount_total:sum'], groupby=['date_order:month'],
                               orderby='date_order asc')
        if not data:
            return [] 
        else:
            # Create a list of all 12 months
            months = list(calendar.month_name)[1:]

            # Create a dictionary to store the data for each month
            data_by_month = {month: {} for month in months}

            # Iterate over the data and append each entry to the corresponding month
            for entry in data:
                month_name = datetime.datetime.strptime(entry["date_order:month"], "%B %Y").strftime("%B")
                data_by_month[month_name] = entry 


            # Add empty entries for months with no data
            for month in months:
                if not data_by_month[month]:
                    data_by_month[month] = {'amount_total': 0, 'date_order:month': month, 'date_order_count': 0}


            # Convert the dictionary to a list of dictionaries
            result = [{'month': month, 'data': data_by_month[month]} for month in months]
        return result

    # gets most commonly bought products
    @api.model
    def get_most_common(self):
        query = """
                SELECT full_product_name, COUNT(*) AS count
                FROM pos_order_line
                GROUP BY full_product_name
                ORDER BY count DESC
                LIMIT 5
            """
        self.env.cr.execute(query)
        result = self.env.cr.fetchall()
        output = [{'name': row[0], 'count': row[1]} for row in result]
        return output
