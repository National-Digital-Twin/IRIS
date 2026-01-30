import { HttpParams, provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { BACKEND_API_ENDPOINT } from '@core/tokens/backend-endpoint.token';
import { SEARCH_ENDPOINT } from '@core/tokens/search-endpoint.token';
import { tap } from 'rxjs';
import { FilterPanelService, panelNames } from './filter-panel.service';

const filterData = {
    postcode: ['SW4', 'SW3', 'W14', 'SW8', 'SW1V', 'SW6', 'SW11', 'SW10', 'SW5'],
    built_form: ['Detached', 'MidTerrace', 'EndTerrace', 'EnclosedEndTerrace', 'SemiDetached', 'EnclosedMidTerrace'],
    inspection_year: [
        '2022',
        '2025',
        '2010',
        '2016',
        '2008',
        '2009',
        '2021',
        '2012',
        '2023',
        '2024',
        '2011',
        '2018',
        '2020',
        '2014',
        '2019',
        '2015',
        '2013',
        '2017',
    ],
    energy_rating: ['EPC In Date', 'EPC Expired'],
    fuel_type: ['Biomass', 'SmokelessCoal', 'Oil', 'Coal', 'Electricity', 'Other', 'NaturalFuelGas', 'LPG'],
    window_glazing: ['TripleGlazing', 'SingleGlazing', 'DoubleGlazingAfter2002', 'DoubleGlazingBefore2002', 'DoubleGlazing', 'SecondaryGlazing'],
    wall_construction: ['SystemBuilt', 'Cob', 'TimberFrame', 'GraniteOrWhinstone', 'SolidBrick', 'Sandstone', 'Wall', 'CavityWall'],
    wall_insulation: ['ExternalInsulation', 'InsulatedWall', 'InternalInsulation'],
    floor_construction: ['OtherPremisesBelowFloor', 'AnotherDwellingBelowFloor', 'Floor', 'SolidFloor', 'Suspended'],
    floor_insulation: ['LimitedFloorInsulation', 'NoInsulationInFloor', 'InsulatedFloor'],
    roof_construction: ['RoofRooms', 'OtherPremisesAbove', 'FlatRoof', 'AnotherDwellingAbove', 'PitchedRoof', 'ThatchedRoof'],
    roof_insulation_location: [
        'LimitedInsulation',
        'InsulatedAssumed',
        'InsulatedAtRafters',
        'NoInsulationassumed',
        'LimitedInsulationAssumed',
        'NoInsulationInRoof',
        'NoInsulationAssumedInRoof',
        'CeilingInsulated',
        'Insulated',
        'ThatchedWithAdditionalInsulation',
        'LoftInsulation',
        'InsulatedWithThatched',
    ],
    roof_insulation_thickness: [
        '300mm',
        '200mm',
        '300+mm',
        '400+mm',
        '0mm',
        '400mm',
        '100mm',
        '350mm',
        '12mm',
        '25mm',
        '250mm',
        '75mm',
        '50mm',
        '150mm',
        '270mm',
    ],
    roof_material: ['Metal', 'Unknown', 'GreenRoof', 'GlassOrPolycarbonate', 'TileOrStoneOrSlate', 'Mixed', 'WaterproofMembraneOrConcrete'],
    has_roof_solar_panels: ['HasSolarPanels', 'NoSolarPanels'],
    roof_aspect_area_direction: ['SouthEast', 'West', 'NorthEast', 'North', 'NorthWest', 'SouthWest', 'East', 'South'],
};

describe('DataService', () => {
    let service: FilterPanelService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                provideHttpClient(),
                provideHttpClientTesting(),
                FilterPanelService,
                { provide: SEARCH_ENDPOINT, useValue: '' },
                { provide: BACKEND_API_ENDPOINT, useValue: '' },
            ],
        });

        service = TestBed.inject(FilterPanelService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('retrieveFilterPanels', () => {
        it('should create and return the list of panels with its filters', (done) => {
            service
                .retrieveFilterPanels({ minX: 1, maxX: 2, minY: 3, maxY: 4 })
                .pipe(
                    tap((result) => {
                        expect(result).toHaveLength(5);
                        panelNames.forEach((name, idx) => expect(result.at(idx)?.title).toEqual(name));
                        [5, 1, 2, 2, 6].forEach((size, idx) => expect(result.at(idx)?.filters).toHaveLength(size));
                    }),
                )
                .subscribe({
                    next: () => done(),
                    error: (err) => done(err),
                });

            const params = new HttpParams().set('min_lat', '1').set('max_lat', '2').set('min_long', '3').set('max_long', '4');

            const req = httpMock.expectOne(`/api/filter-summary?${params.toString()}`);
            expect(req.request.method).toBe('GET');
            req.flush(filterData);
        });
    });
});

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
