import { importProvidersFrom } from '@angular/core';
import { Routes } from '@angular/router';
import { PlotlyModule } from 'angular-plotly.js';
import * as PlotlyJS from 'plotly.js-dist-min';
import { DashboardPageComponent } from './dashboard-page.component';

export const DASHBOARD_ROUTES: Routes = [
    {
        path: '',
        pathMatch: 'full',
        redirectTo: 'national',
    },
    {
        path: 'national',
        component: DashboardPageComponent,
        providers: [importProvidersFrom(PlotlyModule.forRoot(PlotlyJS))],
        data: { type: 'national' },
    },
    {
        path: 'area',
        component: DashboardPageComponent,
        providers: [importProvidersFrom(PlotlyModule.forRoot(PlotlyJS))],
        data: { type: 'area' },
    },
];

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
