import { Routes } from '@angular/router';
import { DashboardPageComponent } from '@containers/dashboard/dashboard-page.component';
import { mapStateGuard } from '@core/guards/map-state.guard';
import { ShellComponent } from './containers/shell/shell.component';

export const routes: Routes = [
    {
        path: '',
        component: ShellComponent,
        canActivate: [mapStateGuard],
    },
    {
        path: 'dashboards/national',
        component: DashboardPageComponent,
        data: { type: 'national' },
    },
    {
        path: 'dashboards/area',
        component: DashboardPageComponent,
        data: { type: 'area' },
    },
];

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
