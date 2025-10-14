import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { TimelineDataPoint } from '@core/services/dashboard.service';
import { PlotlyModule } from 'angular-plotly.js';
import type { Config, Data, Layout } from 'plotly.js-dist-min';
import { BaseChartComponent } from '../base-chart.component';

@Component({
    selector: 'c477-sap-timeline-chart',
    imports: [CommonModule, PlotlyModule],
    templateUrl: './sap-timeline-chart.component.html',
    styleUrl: './sap-timeline-chart.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SapTimelineChartComponent extends BaseChartComponent {
    public override readonly chartConfig: Partial<Config> = { responsive: true, displayModeBar: true, displaylogo: false };

    public chartData = signal<Data[]>([]);
    public chartLayout: Partial<Layout> = {};
    public loading = signal(true);

    protected loadData(): void {
        this.loading.set(true);

        const sub = this.dashboardService.getSAPTimeline().subscribe((response) => {
            const { data, layout } = this.buildChart(response.timeline);

            this.chartData.set(data);
            this.chartLayout = layout;
            this.loading.set(false);
        });

        this.subscriptions.add(sub);
    }

    private buildChart(timeline: TimelineDataPoint[]): { data: Data[]; layout: Partial<Layout> } {
        const startIndex = Math.floor(timeline.length * 0.8);
        const startDate = timeline[startIndex]?.date || new Date();
        const endDate = timeline.at(-1)?.date || new Date();

        const data: Data[] = [
            {
                type: 'scatter',
                mode: 'lines',
                x: timeline.map((t) => t.date.toISOString().split('T')[0]),
                y: timeline.map((t) => t.avg_sap_score),
                line: { color: '#000000', width: 1 },
                hovertemplate: '<b>%{x}</b><br>SAP Score: %{y:.1f}<extra></extra>',
            },
        ];

        const layout: Partial<Layout> = {
            margin: { l: 50, r: 15, t: 10, b: 40 },
            xaxis: {
                title: { text: '' },
                type: 'date',
                showgrid: false,
                tickfont: { size: 9 },
                range: [startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0]],
                rangeslider: { visible: true },
            },
            yaxis: {
                title: { text: 'SAP score', font: { size: 10 } },
                range: [50, 100],
                showgrid: true,
                gridcolor: '#e0e0e0',
                tickfont: { size: 9 },
            },
            font: { ...this.chartService.commonFont, size: 10 },
            height: 300,
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
        };

        return { data, layout };
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
