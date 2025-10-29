import { Injectable, Type, inject } from '@angular/core';
import { RUNTIME_CONFIGURATION } from '@core/tokens/runtime-configuration.token';

export const dashboardTypes = ['national', 'area'] as const;
export type DashboardType = (typeof dashboardTypes)[number];

export interface ChartConfig<T = unknown> {
    id: string;
    component: Type<T>;
    gridClass?: string;
}

@Injectable({ providedIn: 'root' })
export class ChartService {
    readonly #config = inject(RUNTIME_CONFIGURATION);

    public get epcColors(): Record<string, string> {
        return this.#config.epcColours;
    }

    public get commonHoverStyle(): { bgcolor: string; font: { color: string; family: string } } {
        return {
            bgcolor: '#000',
            font: { color: 'white', family: 'Roboto, sans-serif' },
        };
    }

    public get commonFont(): { family: string } {
        return { family: 'Roboto, sans-serif' };
    }

    public get colorway(): string[] {
        return ['#3670B3', '#002244', '#FFCF06', '#E02720', '#62BA5A'];
    }

    public sortRegionsAlphabetically<T extends { region_name: string }>(regions: T[]): T[] {
        return [...regions].sort((a, b) => a.region_name.localeCompare(b.region_name));
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
