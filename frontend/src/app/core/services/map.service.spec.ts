import { NgZone, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { MinimapComponent } from '@components/minimap/minimap.component';
import { RUNTIME_CONFIGURATION } from '@core/tokens/runtime-configuration.token';
import mapboxgl from 'mapbox-gl';
import { MapBoxService } from './map.service';
import { SettingsService } from './settings.service';

jest.mock('mapbox-gl', () => ({
    __esModule: true,
    default: {
        Map: jest.fn().mockImplementation(() => ({ on: jest.fn(), once: jest.fn() })),
    },
}));

const runtimeConfig = {
    mapbox: { accessToken: 'pk.runtime-public-token' },
    map: { center: [0, 0] as [number, number], zoom: 6, pitch: 0, bearing: 0, style: { light: 'light-style', dark: 'dark-style' } },
    minimap: { zoom: 8 },
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
        jest.clearAllMocks();
        TestBed.configureTestingModule({
            providers: [
                MapBoxService,
                { provide: RUNTIME_CONFIGURATION, useValue: runtimeConfig },
                { provide: SettingsService, useValue: { get: () => signal('light') } },
            ],
        });

        service = TestBed.inject(MapBoxService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('authenticates the main map with the configured public token', () => {
        service.setup({ ...runtimeConfig.map, style: runtimeConfig.map.style.light });
        const zone = TestBed.inject(NgZone);
        zone.runOutsideAngular(() => zone.onStable.emit());

        expect(mapboxgl.Map).toHaveBeenCalledWith(expect.objectContaining({ container: 'map', accessToken: runtimeConfig.mapbox.accessToken }));
    });

    it('authenticates the minimap with the same configured public token', () => {
        const minimap = TestBed.runInInjectionContext(() => new MinimapComponent());
        minimap.ngOnInit();

        expect(mapboxgl.Map).toHaveBeenCalledWith(expect.objectContaining({ container: 'minimap', accessToken: runtimeConfig.mapbox.accessToken }));
    });
});
