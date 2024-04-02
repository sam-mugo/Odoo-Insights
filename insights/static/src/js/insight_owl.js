/** @odoo-module */


import {useService} from "@web/core/utils/hooks";
import {registry} from "@web/core/registry";
import {ChartRender} from "./chartTemplate";

const {Component} = owl;
const {useState, onWillStart} = owl.hooks;

export class ShortCutsComponent extends Component {
    setup() {
        this.state = useState({
            stockItems: [],
            topCustomers: [],
            weekSales: [],
            topItems: [],
            monthSales: [],
            yearSales: [],
            paidCustomer: [],
            unpaidCustomer: [],
            paidVendor: [],
            unpaidVendor: [],
        });
        this.orm = useService("orm");
        onWillStart(async () => {
            await this.getStock();
            await this.getTopCustomers();
            await this.getWeekSales();
            await this.getTopSelling();
            await this.getMonthlySales();
            await this.getYearSales();
            await this.getPaidCustomerInvoices();
            await this.getUnpaidCustomerInvoices();
            await this.getPaidVendorInvoices();
            await this.getUnpaidVendorInvoices();
        });

    }

    // function to get out stock products
    async getStock() {
        let items = await this.orm.call("pos.order", "get_out_of_stock", []);
        let cleanData = JSON.parse(JSON.stringify(items))
        this.state.stockItems['labels'] = cleanData.map((row) => row.product_id);
        this.state.stockItems['values'] = cleanData.map((row) => row.qty_on_hand);
        this.state.stockItems['values2'] = cleanData.map((row) => row.qty_forecast);
    }

    // function to get top customers
    async getTopCustomers() {
        let customers = await this.orm.call("pos.order", "get_top_customers", []);
        let cleanData = JSON.parse(JSON.stringify(customers))
        this.state.topCustomers['labels'] = cleanData.map((row) => row.name);
        this.state.topCustomers['values'] = cleanData.map((row) => row.total_invoiced)
    }

    // function to get sales for the week
    async getWeekSales() {
        let sales = await this.orm.call("pos.order", "get_all_week", []);
        let cleanData = JSON.parse(JSON.stringify(sales))
        this.state.weekSales['labels'] = cleanData.map((row) => row.day);
        this.state.weekSales['values'] = cleanData.map((row) => row.data.amount_total)
    }

    // function to get top-selling products
    async getTopSelling() {
        let products = await this.orm.call("pos.order", "get_most_common", []);
        let cleanData = JSON.parse(JSON.stringify(products))
        this.state.topItems['labels'] = cleanData.map((row) => row.name);
        this.state.topItems['values'] = cleanData.map((row) => row.count);
    }

    // function to get sales for the last month(30 days)
    async getMonthlySales() {
        let sales = await this.orm.call("pos.order", "get_all_month", [],);
        let cleanData = JSON.parse(JSON.stringify(sales))
        this.state.monthSales['labels'] = cleanData.map((row) => row.day);
        this.state.monthSales['values'] = cleanData.map((row) => row.data.amount_total);
    }

    // function to get sales for the current year
    async getYearSales() {
        let sales = await this.orm.call("pos.order", "get_all_year", []);
        let cleanData = JSON.parse(JSON.stringify(sales));
        this.state.yearSales['labels'] = cleanData.map((row) => row.month);
        this.state.yearSales['values'] = cleanData.map((row) => row.data.amount_total);
    }

    // function to get paid customer invoices
    async getPaidCustomerInvoices() {
        this.state.paidCustomer = await this.orm.call("account.move", "get_paid_customer_invoices", [],);
    }

    // function to get unpaid customer invoices
    async getUnpaidCustomerInvoices() {
        this.state.unpaidCustomer = await this.orm.call("account.move", "get_unpaid_customer_invoices", [],);
    }

    // function to get paid vendor invoices
    async getPaidVendorInvoices() {
        let invoices = await this.orm.call("account.move", "get_paid_vendor_invoices", [],);
        invoices["total"] = invoices.reduce((accumulator, object) => {
            return accumulator + object.amount_total_signed}, 0);
        this.state.paidVendor = invoices;
    }

    // function to get unpaid vendor invoices
    async getUnpaidVendorInvoices() {
        const vendors = await this.orm.call("account.move", "get_unpaid_vendor_invoices", [],);
        vendors["total"] = vendors.reduce((accumulator, object) => {
            return accumulator + object.amount_total_signed
        }, 0);
        this.state.unpaidVendor = vendors;
    }
}

ShortCutsComponent.template = "insights.Insight";
ShortCutsComponent.components = {ChartRender};

registry
    .category("actions")
    .add("insights.actions_insight", ShortCutsComponent);
