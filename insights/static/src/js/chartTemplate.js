/** @odoo-module */


const {Component} = owl;
const {onWillStart, useRef, onMounted} = owl.hooks;
const {loadJS} = owl.utils;

export class ChartRender extends Component {
    setup() {
        this.chartRef = useRef("chart");

        onWillStart(async () => {
            await loadJS('insights/static/src/lib/chart.umd.min.js')
        });

        onMounted(() => this.renderChart());
    }

    // chart render function
    renderChart() {
        new Chart(this.chartRef.el,
            {
                type: this.props.type,
                data: {
                    labels: this.props.labels,
                    datasets: [
                        {
                            label: this.props.label,
                            data: this.props.data,

                        },
                    ],
                },
                options: {
                    indexAxis: this.props.indexAxis,
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        title: {
                            display: true,

                        },
                    }
                },
            }
        );
    }

}

ChartRender.template = "ht_insights.ChartRender"