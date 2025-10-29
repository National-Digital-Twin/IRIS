import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { TimelineAvgSAPDataPoint } from '@core/services/dashboard.service';
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
    public chartLayout = signal<Partial<Layout>>({});
    public loading = signal(true);

    protected loadData(): void {
        this.loading.set(true);

        const polygon = this.selectedArea?.geometry;
        if (!polygon) {
            return;
        }

        const sub = this.dashboardService.getSAPTimeline(polygon).subscribe((response) => {
            const { data, layout } = this.buildChart(response.timeline);

            this.chartData.set(data);
            this.chartLayout.set(layout);
            this.loading.set(false);
        });

        this.subscriptions.add(sub);
    }

    private buildChart(timeline: TimelineAvgSAPDataPoint[]): { data: Data[]; layout: Partial<Layout> } {
        const ratings = timeline.map((t) => t.avg_sap_rating);
        const minRating = Math.min(...ratings);
        const maxRating = Math.max(...ratings);
        const padding = (maxRating - minRating) * 0.1 || 5; // 10% padding or 5 points minimum

        const data: Data[] = [
            {
                type: 'scatter',
                mode: 'lines',
                x: timeline.map((t) => t.date.toISOString().split('T')[0]),
                y: ratings,
                line: { color: '#000000', width: 2 },
                hovertemplate: '<b>%{x}</b><br>SAP Rating: %{y:.1f}<extra></extra>',
            },
        ];

        const layout: Partial<Layout> = {
            margin: { l: 50, r: 15, t: 10, b: 40 },
            xaxis: {
                title: { text: '' },
                type: 'date',
                showgrid: false,
                tickfont: { size: 9 },
                rangeslider: { visible: true },
            },
            yaxis: {
                title: { text: 'SAP Rating', font: { size: 10 } },
                range: [Math.floor(minRating - padding), Math.ceil(maxRating + padding)],
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
