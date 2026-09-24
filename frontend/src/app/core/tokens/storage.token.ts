import { DOCUMENT } from '@angular/common';
import { InjectionToken, inject } from '@angular/core';

export const STORAGE = new InjectionToken<Storage>('STORAGE', {
    providedIn: 'root',
    factory: (): Storage => inject(DOCUMENT).defaultView!.localStorage,
});

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
