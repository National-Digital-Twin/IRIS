import { Injectable, NgZone, inject, signal } from '@angular/core';
import { RoofAspectAreaDirectionField } from '@core/enums/roof-aspect-area-direction';
import { FilterProps } from '@core/models/advanced-filters.model';
import { BuildingMap, BuildingModel } from '@core/models/building.model';
import { FilterableBuildingModel } from '@core/models/filterable-building.model';
import { MapLayerFilter } from '@core/models/layer-filter.model';
import { SETTINGS, SettingsService } from '@core/services/settings.service';
import { RUNTIME_CONFIGURATION } from '@core/tokens/runtime-configuration.token';
import { MapLayerId } from '@core/types/map-layer-id';
import { booleanWithin } from '@turf/boolean-within';
import { Polygon } from 'geojson';
import { ExpressionSpecification, PaintSpecification } from 'mapbox-gl';
import { DataService } from './data.service';
import { FilterableBuildingService } from './filterable-building.service';
import { MAP_SERVICE, MapLatLng } from './map.token';
import { SpatialQueryService } from './spatial-query.service';

type MapLayerPaintKeys = keyof PaintSpecification;

interface ExpressionAndMapLayerFilter {
    expression: ExpressionSpecification;
    mapLayerFilter: MapLayerFilter & { layerId: MapLayerId };
}

type CurrentExpressions = Record<MapLayerPaintKeys, ExpressionAndMapLayerFilter>;
type ToidBuckets = { flaggedTOIDS: string[]; excludeFromDefault: string[] };

@Injectable({ providedIn: 'root' })
export class UtilService {
    readonly #dataService = inject(DataService);
    readonly #filterableBuildingService = inject(FilterableBuildingService);
    readonly #mapService = inject(MAP_SERVICE);
    readonly #runtimeConfig = inject(RUNTIME_CONFIGURATION);
    readonly #settings = inject(SettingsService);
    readonly #spatialQueryService = inject(SpatialQueryService);
    readonly #zone = inject(NgZone);
    readonly #roofAspectAreaDirectionFieldMap: Record<string, string> = RoofAspectAreaDirectionField;

    private readonly colourBlindMode = this.#settings.get(SETTINGS.ColourBlindMode);

    public multiDwelling = signal<string | undefined>(undefined);
    public selectedCardUPRN = signal<string | undefined>(undefined);
    public selectedUPRN = signal<string | undefined>(undefined);

    private readonly currentMapViewExpressions = signal<CurrentExpressions | undefined>(undefined);
    private readonly filteredBuildings = signal<BuildingMap | undefined>(undefined);
    private readonly filterProps = signal<FilterProps>({});

    public setFilters(filters: FilterProps): void {
        this.filterProps.set(filters);
    }

    /**
     * Create an array of building TOIDS and colours from buildings
     * @param addresses filtered addresses within map bounds
     * @returns MapboxGLJS expression
     */
    public createBuildingColourFilter(): void {
        const unfilteredBuildings = this.#dataService.buildings();
        const filterableBuildingModels = this.#filterableBuildingService.FilterableBuildingModels();

        if (!unfilteredBuildings || !Object.keys(unfilteredBuildings).length) {
            return;
        }

        const filterProps = this.filterProps();
        const buildings = this.filterBuildings(unfilteredBuildings, filterableBuildingModels, filterProps);

        const spatialFilter = this.#spatialQueryService.spatialFilterBounds();
        const filteredBuildings = this.filterBuildingsWithinBounds(buildings, spatialFilter);

        // set the filtered buildings so that the filters can search it
        this.filteredBuildings.set(filteredBuildings);

        /**
         * Get the default colors and patterns
         * for tolids.
         */
        const defaultColor = this.#runtimeConfig.epcColours['default'];
        const defaultPattern = 'default-pattern';

        const expressions = this.#createBaseExpressions();

        const toidBuckets: ToidBuckets = {
            flaggedTOIDS: [],
            excludeFromDefault: [],
        };

        /** Iterate through the filtered toids */
        Object.keys(filteredBuildings).forEach((toid) => {
            /** Get the buildings UPRN's for a TOID */
            const dwellings: BuildingModel[] = filteredBuildings[toid];
            this.#addToidVisuals(toid, dwellings, unfilteredBuildings, defaultColor, defaultPattern, expressions, toidBuckets);
        });

        this.#appendExpressionDefaults(expressions, defaultColor, defaultPattern);

        /** apply the expression to update map layers */
        this.setCurrentMapExpression(expressions);

        this.#syncSelectedDwelling(filteredBuildings);
        this.#syncSelectedBuildingsIfFiltered(filteredBuildings, spatialFilter);
        this.#applyToidFilters(toidBuckets.flaggedTOIDS, toidBuckets.excludeFromDefault);
    }

    #createBaseExpressions(): CurrentExpressions {
        const expressions = {} as CurrentExpressions;
        expressions['fill-extrusion-color'] = {
            mapLayerFilter: {
                layerId: 'OS/TopographicArea_2/Building/1_3D-Single-Dwelling',
                expression: ['all', ['==', '_symbol', 4], ['in', 'TOID']],
            },
            expression: ['match', ['get', 'TOID']],
        };
        expressions['fill-extrusion-pattern'] = {
            mapLayerFilter: {
                layerId: 'OS/TopographicArea_2/Building/1_3D-Multi-Dwelling',
                expression: ['all', ['==', '_symbol', 4], ['in', 'TOID']],
            },
            expression: ['match', ['get', 'TOID']],
        };
        return expressions;
    }

    #addToidExpression(expressions: CurrentExpressions, expressionKey: keyof CurrentExpressions, toid: string, value: string): void {
        expressions[expressionKey].expression.push(toid, value);
        if (!expressions[expressionKey].mapLayerFilter.expression[2].includes(toid)) {
            expressions[expressionKey].mapLayerFilter.expression[2].push(toid);
        }
    }

    #addToidVisuals(
        toid: string,
        dwellings: BuildingModel[],
        unfilteredBuildings: BuildingMap,
        defaultColor: string,
        defaultPattern: string,
        expressions: CurrentExpressions,
        toidBuckets: ToidBuckets,
    ): void {
        if (dwellings.length === 0) {
            this.#addToidExpression(expressions, 'fill-extrusion-color', toid, defaultColor);
            return;
        }

        if (dwellings.length === 1) {
            this.#addSingleDwellingVisuals(toid, dwellings[0], unfilteredBuildings, defaultPattern, expressions, toidBuckets);
            return;
        }

        this.#addMultiDwellingVisuals(toid, dwellings, defaultPattern, expressions, toidBuckets);
    }

    #addSingleDwellingVisuals(
        toid: string,
        dwelling: BuildingModel,
        unfilteredBuildings: BuildingMap,
        defaultPattern: string,
        expressions: CurrentExpressions,
        toidBuckets: ToidBuckets,
    ): void {
        const { EPC, Flagged } = dwelling;
        const color = EPC ? this.getEPCColour(EPC) : defaultPattern;
        if (Flagged) toidBuckets.flaggedTOIDS.push(toid);
        toidBuckets.excludeFromDefault.push(toid);

        const multiDwelling = unfilteredBuildings[toid].length > 1;
        if (multiDwelling) {
            const pattern = EPC ? this.getEPCPattern([EPC]) : defaultPattern;
            this.#addToidExpression(expressions, 'fill-extrusion-pattern', toid, pattern);
            return;
        }
        this.#addToidExpression(expressions, 'fill-extrusion-color', toid, color);
    }

    #addMultiDwellingVisuals(
        toid: string,
        dwellings: BuildingModel[],
        defaultPattern: string,
        expressions: CurrentExpressions,
        toidBuckets: ToidBuckets,
    ): void {
        const epcs = dwellings.map(({ EPC }) => EPC).filter((epc): epc is NonNullable<BuildingModel['EPC']> => !!epc);
        const flagged = dwellings.some(({ Flagged }) => Flagged);
        const epcStrings = epcs.map((epc) => epc.toString());
        const pattern = epcStrings.length === 0 ? defaultPattern : this.getEPCPattern(epcStrings);
        if (flagged) toidBuckets.flaggedTOIDS.push(toid);
        toidBuckets.excludeFromDefault.push(toid);
        this.#addToidExpression(expressions, 'fill-extrusion-pattern', toid, pattern);
    }

    #appendExpressionDefaults(expressions: CurrentExpressions, defaultColor: string, defaultPattern: string): void {
        expressions['fill-extrusion-color'].expression.push(defaultColor);
        expressions['fill-extrusion-pattern'].expression.push(defaultPattern);
    }

    #syncSelectedDwelling(filteredBuildings: BuildingMap): void {
        const selectedUPRN = this.#dataService.selectedUPRN();
        if (!selectedUPRN) {
            return;
        }

        const exists = this.uprnInFilteredBuildings(selectedUPRN, filteredBuildings);
        if (!exists) {
            this.singleDwellingDeselected();
        }
    }

    #syncSelectedBuildingsIfFiltered(filteredBuildings: BuildingMap, spatialFilter?: mapboxgl.Point[]): void {
        if (Object.keys(this.filterProps()).length || spatialFilter) {
            this.#dataService.setSelectedBuildings(Object.values(filteredBuildings));
        }
    }

    #applyToidFilters(flaggedTOIDS: string[], excludeFromDefault: string[]): void {
        this.#mapService.filterMapLayer({
            layerId: 'OS/TopographicArea_2/Building/1_3D-Dwelling-Flagged',
            expression: ['all', ['==', '_symbol', 4], ['in', 'TOID', ...flaggedTOIDS]],
        });
        this.#mapService.filterMapLayer({
            layerId: 'OS/TopographicArea_2/Building/1_3D',
            expression: ['all', ['==', '_symbol', 4], ['!in', 'TOID', ...excludeFromDefault]],
        });
    }

    /**
     * Get the mean EPC pattern for a TOID.
     *
     * Determins the average EPC rating for a TOID
     * then returns the corresponding EPC pattern.
     */
    public getEPCPattern(epcRatings: string[]): string {
        const colorBlindMode = this.colourBlindMode();
        const meanEPC = this.getMeanEPCValue(epcRatings).toLowerCase();
        return colorBlindMode ? `cb-${meanEPC}-pattern` : `${meanEPC}-pattern`;
    }

    public setCurrentMapExpression(expressions: CurrentExpressions): void {
        this.currentMapViewExpressions.set(expressions);
        this.updateMap();
    }

    public updateMap(): void {
        const currentExpressions = this.currentMapViewExpressions();
        if (currentExpressions === undefined) {
            return;
        }

        /*
         * For each of the expressions, set the
         * corresponding map layer filter and
         * expression for the layer.
         */
        Object.keys(currentExpressions).forEach((key) => {
            const expressionKey = key as keyof PaintSpecification;
            const { expression, mapLayerFilter } = currentExpressions[expressionKey];

            this.#mapService.filterMapLayer(mapLayerFilter);
            this.#mapService.setMapLayerPaint(mapLayerFilter.layerId, expressionKey, expression);
        });
    }

    /**
     *
     * @param epcRatings Array of EPC ratings
     * @returns The mean EPC rating
     */
    public getMeanEPCValue(epcRatings: string[]): string {
        let meanEPC = '';
        // assign a weighting to the EPC ratings
        const weightings: Record<string, number> = {
            A: 1,
            B: 2,
            C: 3,
            D: 4,
            E: 5,
            F: 6,
            G: 7,
        };
        const scores: number[] = [];
        // remove EPC none from the epcs to average
        const epcsToAverage = epcRatings.filter((rating) => rating !== 'none');
        if (epcsToAverage.length > 0) {
            // get the weighting for each epc value
            epcsToAverage.forEach((val) => scores.push(weightings[val]));
            const sum = scores.reduce((a, c) => a + c, 0);
            const mean = sum / scores.length;
            Object.keys(weightings).forEach((epc: string) => {
                // find the corresponding weighting for the mean
                if (Math.round(mean) === weightings[epc]) {
                    meanEPC = epc;
                }
            });
            return meanEPC;
        } else {
            return 'none';
        }
    }

    public getEPCColour(epcRating: string): string {
        const colorBlindMode = this.colourBlindMode();

        if (colorBlindMode) {
            return this.#runtimeConfig.epcColoursCD[epcRating || 'default'];
        } else {
            return this.#runtimeConfig.epcColours[epcRating || 'default'];
        }
    }

    public filterBuildingsWithinBounds(buildings: BuildingMap, spatialQueryBounds?: mapboxgl.Point[]): BuildingMap {
        /** get all features within current map bounds */
        const currentMapFeatures = this.#mapService.queryFeatures();

        // check if there is a user drawn spatial filter
        const spatialFilter = spatialQueryBounds ? this.#spatialQueryService.spatialFilterGeom() : undefined;
        const filteredToids: BuildingMap = {};
        currentMapFeatures
            .filter((feature) => {
                // if there is a spatial filter
                // remove any polygon features outside of
                // the filter geometry
                if (feature.geometry.type === 'Polygon') {
                    return spatialFilter ? booleanWithin(feature.geometry as Polygon, spatialFilter?.geometry as Polygon) : feature;
                }

                return false;
            })
            .sort((a, b) => (a.properties!.TOID < b.properties!.TOID ? -1 : 1))
            .map((feature) => {
                const building = buildings[feature.properties!.TOID];
                if (building) {
                    filteredToids[feature.properties!.TOID] = building;
                }
            });
        return filteredToids;
    }

    /**
     * This filters the building data by the user selected
     * filters
     * @param buildings all buildings data
     * @returns BuildingMap of filtered buildings
     */
    public filterBuildings(buildings: BuildingMap, filterableBuildingModels: FilterableBuildingModel[], filterProps: FilterProps): BuildingMap {
        if (Object.keys(filterProps).length === 0) {
            return buildings;
        }

        // convert building object to array to ease filtering
        const buildingsArray = Array.from(Object.values(buildings).flat());
        const filterKeys = Object.keys(filterProps) as Array<keyof FilterProps>;
        // filter buildings
        const filteredUprns = new Set(
            filterableBuildingModels
                .filter((filterableBuildingModel: FilterableBuildingModel) =>
                    filterKeys.every((key) => {
                        return this.#matchesFilterKey(filterableBuildingModel, buildingsArray, filterProps, key);
                    }),
                )
                .map((filteredDetailedBuildingModel) => filteredDetailedBuildingModel.UPRN),
        );
        const filtered = buildingsArray.filter((building) => filteredUprns.has(building.UPRN));
        const filteredBuildings: BuildingMap = this.#dataService.mapBuildings(filtered);
        return filteredBuildings;
    }

    #matchesFilterKey(
        filterableBuildingModel: FilterableBuildingModel,
        buildingsArray: BuildingModel[],
        filterProps: FilterProps,
        key: keyof FilterProps,
    ): boolean {
        const selectedFilterValues = filterProps[key];
        if (!selectedFilterValues?.length) {
            return true;
        }

        // remove additional quotes for year filter
        // may not need this any more?
        const removeQuotes = selectedFilterValues.map((item) => item.replace(/['"]+/g, ''));
        if (key === 'Flagged') {
            return filterableBuildingModel.Flagged;
        }
        if (key === 'EPCExpiry') {
            return this.#matchesEpcExpiry(filterableBuildingModel, selectedFilterValues);
        }
        if (key === 'StructureUnitType' || key === 'EPC') {
            return this.#matchesBuildingModelField(filterableBuildingModel, buildingsArray, key, removeQuotes);
        }
        return this.#matchesFilterableBuildingField(filterableBuildingModel, key, removeQuotes);
    }

    #matchesEpcExpiry(filterableBuildingModel: FilterableBuildingModel, selectedFilterValues: string[]): boolean {
        const lodgementDate = filterableBuildingModel.LodgementDate;
        if (!lodgementDate) {
            return false;
        }

        const tenYearsAgo = new Date();
        tenYearsAgo.setFullYear(tenYearsAgo.getFullYear() - 10);
        const isExpired = new Date(lodgementDate) < tenYearsAgo;
        return (selectedFilterValues.includes('EPC Expired') && isExpired) || (selectedFilterValues.includes('EPC In Date') && !isExpired);
    }

    #matchesBuildingModelField(
        filterableBuildingModel: FilterableBuildingModel,
        buildingsArray: BuildingModel[],
        key: 'StructureUnitType' | 'EPC',
        removeQuotes: string[],
    ): boolean {
        const matchedBuildingModel = buildingsArray.find((building) => building.UPRN === filterableBuildingModel.UPRN);
        if (!matchedBuildingModel) {
            return false;
        }

        // eslint-disable-next-line
        // @ts-ignore
        return removeQuotes.includes(matchedBuildingModel[key as keyof BuildingModel]);
    }

    #matchesFilterableBuildingField(filterableBuildingModel: FilterableBuildingModel, key: keyof FilterProps, removeQuotes: string[]): boolean {
        if (key === 'RoofAspectAreaDirection') {
            return removeQuotes
                .map((direction) => filterableBuildingModel[this.#roofAspectAreaDirectionFieldMap[direction] as keyof FilterableBuildingModel])
                .every((fieldValue) => !!fieldValue);
        }

        let mappedKeys = removeQuotes;
        if (key === 'RoofHasSolarPanels') {
            mappedKeys = removeQuotes.map((value) => {
                if (value === 'HasSolarPanels') return 'true';
                if (value === 'NoSolarPanels') return 'false';
                return '';
            });
            return mappedKeys.includes(filterableBuildingModel.HasRoofSolarPanels?.toString() ?? '');
        }

        // eslint-disable-next-line
        // @ts-ignore
        return mappedKeys.includes(filterableBuildingModel[key as keyof FilterableBuildingModel]?.toString());
    }

    public epcExpired(lodgementDate?: string): boolean {
        if (!lodgementDate) {
            return false;
        }
        const tenYearsAgo = new Date();
        tenYearsAgo.setFullYear(tenYearsAgo.getFullYear() - 10);
        return new Date(lodgementDate) < tenYearsAgo;
    }

    public epcInDate(lodgementDate?: string): boolean {
        if (!lodgementDate) {
            return false;
        }
        const tenYearsAgo = new Date();
        tenYearsAgo.setFullYear(tenYearsAgo.getFullYear() - 10);
        return new Date(lodgementDate) >= tenYearsAgo;
    }

    /**
     * Find buildings based on TOID
     * @param toid toid of building
     * @returns array of buildings associated with toid
     */
    public getBuildings(toid: string): BuildingModel[] {
        const allBuildings = this.#dataService.buildings();
        if (!allBuildings) {
            return [];
        }
        const buildings = allBuildings[toid];
        if (buildings) {
            return buildings.flat();
        }
        return [];
    }

    public uprnInFilteredBuildings(uprn: string, buildings: BuildingMap): boolean {
        return Object.values(buildings)
            .flat()
            .some((b) => b.UPRN === uprn);
    }

    /**
     * Splits a full address and returns part
     * of the address
     * @param address full address string
     * @param index index of address part to return after
     * address is split
     * @returns address part
     */
    public splitAddress(index: number, fullAddress?: string): string {
        if (!fullAddress) {
            return '';
        }
        return fullAddress.split(',')[index];
    }

    /**
     * Create a histogram of EPC counts for a ward
     * @param ratings EPC counts for a ward
     * @returns
     */
    public createHistogram(ratings: Array<{ rating: string; count: number }>): string {
        // wmax value of the histogram array
        const maxValue = Math.max(...ratings.map((o) => o.count));
        const labels: string[] = [];
        const histogram = ratings.map((r) => {
            // getting a percentage of the max
            const height = (r.count / maxValue) * 100;
            const label = `<span>${r.rating === 'none' ? 'No EPC*' : r.rating}</span>`;
            labels.push(label);
            return `
                <div class="bar" style="height: calc(${height}% + 5px)">
                    <span class="rating">${r.count}</span>
                    <div class="line" style="background: ${this.getEPCColour(r.rating)}"></div>
                </div>
            `;
        });

        return `
            <div class="histogram">
                <div class="chart">${histogram.join('')}</div>
                <div class="labels">${labels.join('')}</div>
            </div>
        `;
    }

    /**
     * Handle selecting of results card in results list
     * @param TOID
     * @param UPRN
     */
    public resultsCardSelected(TOID: string, UPRN: string): void {
        /** select single dwelling on map */
        if (UPRN !== '' && TOID !== '') {
            this.selectResultsCard(UPRN);
            this.selectSingleDwellingOnMap(TOID);
        }
        /** select multi-dwelling on map */
        if (UPRN === '' && TOID !== '') {
            this.selectMultiDwellingOnMap(TOID);
        }
    }

    /**
     * Handle deselecting results card in results list
     */
    public resultsCardDeselected(): void {
        /**
         * if multi-dwelling don't deselect
         * building on map
         */
        if (this.multiDwelling() !== undefined) {
            this.deselectResultsCard();
            this.closeBuildingDetails();
            this.multiDwelling.set(undefined);
            this.deselectMultiDwellingOnMap();
        } else {
            this.deselectResultsCard();
            this.closeBuildingDetails();
            this.deselectSingleDwellingOnMap();
        }
    }

    /**
     * Handle clicking 'View Details' button
     * @param TOID
     * @param UPRN
     * @param mapCenter
     */
    public viewDetailsButtonClick(TOID: string, UPRN: string, mapCenter: MapLatLng): void {
        /** if its not viewing details for a multi dwelling select on map */
        if (this.multiDwelling() === undefined) {
            this.selectSingleDwellingOnMap(TOID);
        }
        this.selectResultsCard(UPRN);
        this.viewBuildingDetails(UPRN);
        /** if filtered data also zoom map */
        const filterProps = this.filterProps();
        if (Object.keys(filterProps).length) {
            this.#mapService.zoomToCoords(mapCenter);
        }
    }

    /**
     * Handle 'View Details' close button click
     */
    public closeDetailsButtonClick(): void {
        this.closeBuildingDetails();
        /** if not filtered data or spatial selection also clear map */
        const filterProps = this.filterProps();
        const spatialFilter = this.#spatialQueryService.spatialFilterEnabled();
        if (!spatialFilter && !Object.keys(filterProps).length && this.multiDwelling() === undefined) {
            this.deselectSingleDwellingOnMap();
        }
    }

    /**
     * Handle clicking a single dwelling building on the map
     * @param TOID
     * @param UPRN
     */
    public singleDwellingSelectedOnMap(TOID: string, UPRN: string): void {
        this.selectedUPRN.set(UPRN);
        this.multiDwellingDeselected();
        this.selectSingleDwellingOnMap(TOID);
        this.viewBuildingDetails(UPRN);
        /** if filtered data then results panel open so select card */
        const filterProps = this.filterProps();
        const spatialFilter = this.#spatialQueryService.spatialFilterEnabled();
        if (spatialFilter || Object.keys(filterProps).length) {
            this.selectResultsCard(UPRN);
        }
    }

    /**
     * Handle deselecting a single dwelling building on the map
     */
    public singleDwellingDeselected(): void {
        this.selectedUPRN.set(undefined);
        this.deselectSingleDwellingOnMap();
        this.closeBuildingDetails();
        /** if filtered data then results panel open so deselect card*/
        const spatialFilter = this.#spatialQueryService.spatialFilterEnabled();
        const filterProps = this.filterProps();
        if (spatialFilter || Object.keys(filterProps).length) {
            this.deselectResultsCard();
        }
    }

    /**
     * Handle clicking a multi-dwelling building on the map
     * @param TOID
     */
    public multipleDwellingSelectedOnMap(TOID: string): void {
        this.singleDwellingDeselected();
        this.selectMultiDwellingOnMap(TOID);
    }

    /**
     * Handle deselecting a multi-dwelling building on the map
     */
    public multiDwellingDeselected(): void {
        this.multiDwelling.set(undefined);
        this.deselectMultiDwellingOnMap();
        this.deselectResultsCard();
    }

    public setSpatialFilter(searchArea: GeoJSON.Feature<Polygon>): void {
        this.#dataService.setSelectedUPRN(undefined);
        this.#dataService.setSelectedBuilding(undefined);
        this.#spatialQueryService.setSelectedTOID('');

        /** clear building layer selections */
        this.#spatialQueryService.selectBuilding('', true);
        this.#spatialQueryService.selectBuilding('', false);
        this.#spatialQueryService.setSpatialGeom(searchArea);
    }

    /**
     * Handle deleting spatial filter
     */
    public deleteSpatialFilter(): void {
        this.singleDwellingDeselected();
        this.multiDwellingDeselected();
        this.#spatialQueryService.setSpatialGeom(undefined);
        this.#spatialQueryService.setSpatialFilter(false);
        this.#spatialQueryService.setSpatialFilterBounds(undefined);
        this.#mapService.drawControl?.deleteAll();
        this.#zone.run(() => this.closeResultsPanel());
    }

    /**
     * Handle closing of results panel
     */
    public closeResultsPanel(): void {
        this.#dataService.setSelectedBuildings(undefined);
    }

    /** set the UPRN of the selected results card */
    private selectResultsCard(UPRN: string): void {
        this.selectedCardUPRN.set(UPRN);
    }

    private deselectResultsCard(): void {
        this.selectedCardUPRN.set(undefined);
        this.closeBuildingDetails();
    }

    private viewBuildingDetails(UPRN: string): void {
        this.#dataService.setSelectedUPRN(UPRN);
        const building = this.#dataService.getBuildingByUPRN(UPRN.toString());
        this.#dataService.setSelectedBuilding(building);
    }

    private closeBuildingDetails(): void {
        this.#dataService.setSelectedUPRN(undefined);
        this.#dataService.setSelectedBuilding(undefined);
    }

    private selectSingleDwellingOnMap(TOID: string): void {
        this.#spatialQueryService.setSelectedTOID(TOID);
        /** single dwelling building */
        this.#spatialQueryService.selectBuilding(TOID, false);
        this.#spatialQueryService.selectBuilding('', true);
    }

    private selectMultiDwellingOnMap(TOID: string): void {
        this.multiDwelling.set(TOID);
        this.#spatialQueryService.setSelectedTOID(TOID);
        /** multi-dwelling building */
        this.#spatialQueryService.selectBuilding('', false);
        this.#spatialQueryService.selectBuilding(TOID, true);

        /** only open results panel if there are no filters */
        const filterProps = this.filterProps();
        const spatialFilter = this.#spatialQueryService.spatialFilterEnabled();
        if (!spatialFilter && !Object.keys(filterProps).length) {
            const buildings = this.getBuildings(TOID);
            this.openResultsPanel(buildings);
        }
    }

    private deselectSingleDwellingOnMap(): void {
        this.#spatialQueryService.setSelectedTOID('');
        /** single-dwelling building */
        this.#spatialQueryService.selectBuilding('', false);
    }

    private deselectMultiDwellingOnMap(): void {
        /** if filtered data then results panel open */
        const filterProps = this.filterProps();
        const spatialFilter = this.#spatialQueryService.spatialFilterEnabled();
        if (!spatialFilter && !Object.keys(filterProps).length) {
            this.closeBuildingDetails();
            this.#zone.run(() => this.closeResultsPanel());
        }
        this.#spatialQueryService.setSelectedTOID('');
        /** multi-dwelling building */
        this.#spatialQueryService.selectBuilding('', true);
    }

    private openResultsPanel(buildings: BuildingModel[]): void {
        this.#dataService.setSelectedBuildings([buildings]);
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
