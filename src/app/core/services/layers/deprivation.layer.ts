import { LAYER_COLORS } from '@core/config/layer-colors.config';
import { DemographicsDataService, DeprivationLayerProperties } from '@core/services/demographics-data.service';
import { FeatureCollection, Geometry } from 'geojson';
import * as mapboxgl from 'mapbox-gl';
import { LayerSpecification, MapMouseEvent } from 'mapbox-gl';
import { firstValueFrom } from 'rxjs';
import { AbstractClimateLayer } from './climate-layer.abstract';

export class DeprivationLayer extends AbstractClimateLayer<DeprivationLayerProperties> {
    private currentPopup?: mapboxgl.Popup;

    constructor(private readonly demographicsDataService: DemographicsDataService) {
        super();
    }

    public get id(): string {
        return 'deprivation-layer';
    }

    public getLayerConfig(): LayerSpecification {
        if (this.maxValues) {
            const { min, max } = this.maxValues;
            return this.createLayerConfig(min, max, LAYER_COLORS.deprivation);
        }

        return this.createLayerConfig(0, 100, LAYER_COLORS.deprivation);
    }

    public async getSourceData(): Promise<FeatureCollection<Geometry, DeprivationLayerProperties>> {
        try {
            if (!this.data) {
                const result = await firstValueFrom(this.demographicsDataService.getDeprivationLayerData());
                if (result) {
                    this.data = result;
                } else {
                    return this.createEmptyFeatureCollection();
                }
            }

            return this.createFeatureCollectionFromData('dep_pct_4');
        } catch (error) {
            console.error(`[DeprivationLayer] Error in getSourceData:`, error);
            return this.createEmptyFeatureCollection();
        }
    }

    public override onLayerClick = (event: MapMouseEvent): void => {
        event.preventDefault();

        const feature = event.features?.[0];
        if (!feature) {
            return;
        }

        const properties = feature.properties as DeprivationLayerProperties;
        const areaName = properties.area_nm?.trim() || 'this area';

        if (this.currentPopup) {
            this.mapService.removePopup(this.currentPopup);
        }

        const popupContent = `
            <div class="popup deprivation-popup">
                <div class="popup-header">
                    <h3>${this.formatPercentage(properties.dep_pct_4)} of households in ${areaName} are deprived in four dimensions</h3>
                    <div class="info-tooltip-container">
                        <button class="info-button" onclick="togglePopoutInfo()">
                            <span class="info-icon">i</span>
                        </button>
                        <div id="popout-info" class="info-tooltip" style="display: none;">
                            <div class="info-tooltip-header">Household deprivation</div>
                            <p>The dimensions of deprivation used to classify households are indicators based on four selected household characteristics.</p>
                            <ul>
                                <li>Education</li>
                                <li>Employment</li>
                                <li>Health</li>
                                <li>Housing</li>
                            </ul>
                            <p>Data comes from the 2021 Census.</p>
                            <button class="close-button" onclick="hidePopoutInfo()">Close</button>
                        </div>
                    </div>
                </div>
                ${this.createHistogram(properties)}
            </div>
        `;

        this.currentPopup = new mapboxgl.Popup({
            closeButton: true,
            closeOnClick: false,
            maxWidth: '400px',
        })
            .setLngLat(event.lngLat)
            .setHTML(popupContent);

        this.currentPopup.on('close', () => {
            this.currentPopup = undefined;
            this.clearFeatureHighlight(event.target);
        });

        this.mapService.registerPopup(this.currentPopup);

        this.highlightFeature(event.target, feature.id);
    };

    private createHistogram(properties: DeprivationLayerProperties): string {
        const bars = [
            { label: 'Deprived in four dimensions', value: properties.dep_pct_4 ?? 0, color: '#080C54' },
            { label: 'Deprived in three dimensions', value: properties.dep_pct_3 ?? 0, color: '#547064' },
            { label: 'Deprived in two dimensions', value: properties.dep_pct_2 ?? 0, color: '#819774' },
            { label: 'Deprived in one dimension', value: properties.dep_pct_1 ?? 0, color: '#A7BE84' },
            { label: 'Not deprived in any dimensions', value: properties.dep_pct_0 ?? 0, color: '#CDE594' },
        ];

        const maxValue = Math.max(...bars.map((b) => b.value), 1);

        const barHtml = bars
            .map((bar) => {
                const height = (bar.value / maxValue) * 100;
                return `
                    <div class="bar" style="height: calc(${height}% + 5px)">
                        <span class="rating">${this.formatPercentage(bar.value)}</span>
                        <div class="line" style="background: ${bar.color}"></div>
                    </div>
                `;
            })
            .join('');

        const labelsHtml = bars.map((bar) => `<span>${bar.label}</span>`).join('');

        return `
            <div class="histogram deprivation-histogram">
                <div class="chart">${barHtml}</div>
                <div class="labels">${labelsHtml}</div>
            </div>
        `;
    }

    private highlightFeature(map: mapboxgl.Map, featureId: string | number | undefined): void {
        if (featureId === undefined || featureId === null) {
            return;
        }

        map.setPaintProperty(this.id, 'fill-opacity', ['case', ['==', ['id'], featureId], 0.9, 0.6]);

        const outlineLayerId = `${this.id}-outline`;

        if (map.getLayer(outlineLayerId)) {
            map.removeLayer(outlineLayerId);
        }

        map.addLayer({
            id: outlineLayerId,
            type: 'line',
            source: `${this.id}-source`,
            paint: {
                'line-color': '#6666aa',
                'line-width': 3,
                'line-opacity': 0.75,
            },
            filter: ['==', ['id'], featureId],
        });
    }

    private clearFeatureHighlight(map: mapboxgl.Map): void {
        map.setPaintProperty(this.id, 'fill-opacity', LAYER_COLORS.deprivation.opacity);

        const outlineLayerId = `${this.id}-outline`;
        if (map.getLayer(outlineLayerId)) {
            map.removeLayer(outlineLayerId);
        }
    }

    private formatPercentage(value: number | undefined): string {
        if (typeof value !== 'number' || Number.isNaN(value)) {
            return '0%';
        }

        return `${value.toFixed(1)}%`;
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
