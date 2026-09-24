import { InjectionToken } from '@angular/core';

export const STORAGE_KEY = new InjectionToken('STORAGE_KEY', {
    providedIn: 'root',
    factory: (): string => 'settings',
});

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
