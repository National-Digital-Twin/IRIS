import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { EPCRegionData } from '@core/services/dashboard.service';
import { PlotlyModule } from 'angular-plotly.js';
import type { Data, Layout } from 'plotly.js-dist-min';
import { BaseChartComponent } from '../base-chart.component';
import { RegionSelectorComponent } from '../shared/region-selector.component';

@Component({
    selector: 'c477-epc-region-chart',
    imports: [CommonModule, PlotlyModule, MatFormFieldModule, MatSelectModule, RegionSelectorComponent],
    templateUrl: './epc-region-chart.component.html',
    styleUrl: './epc-region-chart.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EpcRegionChartComponent extends BaseChartComponent {
    public chartData = signal<Data[]>([]);
    public chartLayout: Partial<Layout> = {};
    public loading = signal(true);

    public selectedRegions = signal<string[]>(['North West', 'North East', 'West Midlands', 'East Midlands']);

    public onRegionChange(regions: string[]): void {
        this.selectedRegions.set(regions);
        this.loadData();
    }

    protected loadData(): void {
        this.loading.set(true);

        const sub = this.dashboardService.getEPCByRegion().subscribe((regionData) => {
            const { data, layout } = this.buildChart(regionData, this.selectedRegions());

            this.chartData.set(data);
            this.chartLayout = layout;
            this.loading.set(false);
        });

        this.subscriptions.add(sub);
    }

    private buildChart(regionData: EPCRegionData[], selectedRegions: string[]): { data: Data[]; layout: Partial<Layout> } {
        const filteredData = regionData.filter((r) => selectedRegions.includes(r.region_name));
        const sortedData = this.chartService.sortRegionsAlphabetically(filteredData);

        const ratings = ['G', 'F', 'E', 'D', 'C', 'B', 'A'];
        const regionNames = sortedData.map((r) => r.region_name);
        const data: Data[] = ratings.map((rating) => ({
            type: 'bar',
            name: rating,
            x: regionNames,
            y: sortedData.map((r) => r[`epc_${rating.toLowerCase()}` as keyof EPCRegionData] || 0),
            marker: { color: this.chartService.epcColors[rating] },
            hoverlabel: this.chartService.commonHoverStyle,
            hovertemplate: '<b>%{x}</b><br>%{y:,}<extra></extra>',
            width: 0.5,
        }));

        const maxTotal = Math.max(
            ...sortedData.map((r) => ratings.reduce((acc, curr) => acc + ((r[`epc_${curr.toLowerCase()}` as keyof EPCRegionData] as number) || 0), 0)),
        );

        const layout: Partial<Layout> = {
            barmode: 'stack',
            margin: { l: 20, r: 40, t: 20, b: 80 },
            xaxis: {
                title: { text: '' },
                tickangle: 'auto',
                tickfont: { size: 11, color: '#333' },
                automargin: true,
            },
            yaxis: {
                title: { text: '' },
                range: [0, maxTotal * 1.1],
                tickformat: '.2s',
                showgrid: true,
                gridcolor: '#e0e0e0',
                side: 'right',
            },
            font: this.chartService.commonFont,
            height: 250,
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            showlegend: true,
            legend: {
                orientation: 'h',
                x: 0.5,
                y: -0.3,
                xanchor: 'center',
                yanchor: 'top',
                traceorder: 'reversed',
            },
        };

        return { data, layout };
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
