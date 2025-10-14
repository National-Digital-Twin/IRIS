import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { RegionCharacteristicData } from '@core/services/dashboard.service';
import { PlotlyModule } from 'angular-plotly.js';
import type { Data, Layout } from 'plotly.js-dist-min';
import { BaseChartComponent } from '../base-chart.component';
import { RegionSelectorComponent } from '../shared/region-selector.component';

@Component({
    selector: 'c477-characteristics-chart',
    imports: [CommonModule, PlotlyModule, MatFormFieldModule, MatSelectModule, RegionSelectorComponent],
    templateUrl: './characteristics-chart.component.html',
    styleUrl: './characteristics-chart.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CharacteristicsChartComponent extends BaseChartComponent {
    public readonly characteristicOptions = [
        { value: 'double glazing', label: 'Double Glazing' },
        { value: 'single glazing', label: 'Single Glazing' },
        { value: 'cavity wall', label: 'Cavity Wall' },
        { value: 'solar panels', label: 'Solar Panels' },
        { value: 'pitched roof', label: 'Pitched Roof' },
        { value: 'solid floor', label: 'Solid Floor' },
        { value: 'roof insulation 150mm', label: 'Roof Insulation 150mm' },
        { value: 'roof insulation 200mm', label: 'Roof Insulation 200mm' },
        { value: 'roof insulation 250mm', label: 'Roof Insulation 250mm' },
    ];

    public chartData = signal<Data[]>([]);
    public chartLayout: Partial<Layout> = {};
    public loading = signal(true);

    public selectedCharacteristic = signal('double glazing');
    public selectedRegions = signal<string[]>(['East Midlands', 'North East', 'West Midlands', 'North West']);

    public onCharacteristicChange(characteristic: string): void {
        this.selectedCharacteristic.set(characteristic);
        this.loadData();
    }

    public onRegionChange(regions: string[]): void {
        this.selectedRegions.set(regions);
        this.loadData();
    }

    protected loadData(): void {
        this.loading.set(true);

        const sub = this.dashboardService.getBuildingCharacteristics(this.selectedCharacteristic()).subscribe((response) => {
            const { data, layout } = this.buildChart(this.selectedCharacteristic(), response.regions, this.selectedRegions());

            this.chartData.set(data);
            this.chartLayout = layout;
            this.loading.set(false);
        });

        this.subscriptions.add(sub);
    }

    private buildChart(characteristic: string, regions: RegionCharacteristicData[], selectedRegions: string[]): { data: Data[]; layout: Partial<Layout> } {
        const filteredRegions = regions.filter((r) => selectedRegions.includes(r.region_name));
        const sortedRegions = this.chartService.sortRegionsAlphabetically(filteredRegions);

        const data: Data[] = [
            {
                type: 'bar',
                x: sortedRegions.map((r) => r.region_name),
                y: sortedRegions.map((r) => r.percentage),
                marker: { color: '#5729CE' },
                text: sortedRegions.map((r) => `${Math.round(r.percentage)}%`),
                textposition: 'auto',
                textfont: { color: 'white', size: 14, family: 'Roboto, sans-serif' },
                hovertemplate: '<b>%{x}</b><br>%{y:.1f}% of buildings have ' + characteristic + '<extra></extra>',
                hoverlabel: this.chartService.commonHoverStyle,
                width: 0.5,
            },
        ];

        const maxPercentage = Math.max(...sortedRegions.map((r) => r.percentage));
        const layout: Partial<Layout> = {
            margin: { l: 40, r: 20, t: 20, b: 80 },
            xaxis: {
                title: { text: '' },
                tickangle: 'auto',
                tickfont: { size: 11, color: '#333' },
                automargin: true,
            },
            yaxis: {
                title: { text: '' },
                range: [0, maxPercentage * 1.15],
                visible: false,
            },
            font: this.chartService.commonFont,
            height: 250,
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            showlegend: false,
        };

        return { data, layout };
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
