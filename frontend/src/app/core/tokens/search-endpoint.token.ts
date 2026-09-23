import { InjectionToken } from '@angular/core';
import { environment } from '@environment';

export const SEARCH_ENDPOINT = new InjectionToken<string>('SEARCH_ENDPOINT', {
    factory: (): string => `${environment.sparql.url}`,
});

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
