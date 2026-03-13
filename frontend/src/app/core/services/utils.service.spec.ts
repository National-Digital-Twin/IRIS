import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { RUNTIME_CONFIGURATION } from '@core/tokens/runtime-configuration.token';
import { MAP_SERVICE } from './map.token';
import { UtilService } from './utils.service';

describe('UtilService', () => {
    let service: UtilService;
    const mapService = {};
    const runtimeConfig = {};

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                UtilService,
                { provide: MAP_SERVICE, useValue: mapService },
                provideHttpClient(),
                provideHttpClientTesting(),
                { provide: RUNTIME_CONFIGURATION, useValue: runtimeConfig },
            ],
        });

        service = TestBed.inject(UtilService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
