import { TestBed } from '@angular/core/testing';
import { RUNTIME_CONFIGURATION } from '@core/tokens/runtime-configuration.token';
import { MapBoxService } from './map.service';

const runtimeConfig = {
    mapLayers: [],
    epcColours: {
        A: '#00ff00',
        B: '#0000ff',
        C: '#ff0000',
    },
    epcColoursCD: {
        A: '#000000',
        B: '#222222',
        C: '#444444',
    },
};

describe('MapService', () => {
    let service: MapBoxService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [MapBoxService, { provide: RUNTIME_CONFIGURATION, useValue: runtimeConfig }],
        });

        jest.mock('mapbox-gl', () => {});

        service = TestBed.inject(MapBoxService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
