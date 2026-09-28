import { InjectionToken } from '@angular/core';

export const BACKEND_API_ENDPOINT = new InjectionToken<string>('BACKEND_API_ENDPOINT', {
    providedIn: 'root',
    factory: (): string => `/api`,
});

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
