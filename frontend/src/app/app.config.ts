import { provideHttpClient } from '@angular/common/http';
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { MapBoxService } from '@core/services/map.service';
import { MAP_SERVICE } from '@core/services/map.token';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
    providers: [
        provideHttpClient(),
        provideRouter(routes, withComponentInputBinding()),
        { provide: MAP_SERVICE, useClass: MapBoxService },
        provideZoneChangeDetection(),
    ],
};

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
