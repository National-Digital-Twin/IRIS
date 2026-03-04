import { TestBed } from '@angular/core/testing';
import { MAP_SERVICE } from './map.token';
import { SpatialQueryService } from './spatial-query.service';

describe('SpatialQueryService', () => {
    let service: SpatialQueryService;
    const mapService = {};

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [SpatialQueryService, { provide: MAP_SERVICE, useValue: mapService }],
        });

        service = TestBed.inject(SpatialQueryService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
