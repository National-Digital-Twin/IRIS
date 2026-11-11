import { RuntimeConfigurationModel } from '@core/models/runtime-configuration.model';
import { environment } from '@environment';

export const loadRuntimeConfiguration = async (fetchConfiguration: typeof fetch = fetch): Promise<RuntimeConfigurationModel> => {
    const proxyUrl = environment.transparent_proxy.url.replace(/\/$/, '');
    const [configResponse, mapboxResponse] = await Promise.all([
        fetchConfiguration('configuration/config.json'),
        fetchConfiguration(`${proxyUrl}/mapbox-config`, { cache: 'no-store' }),
    ]);
    if (!configResponse.ok) {
        throw new Error(`Unable to load IRIS runtime configuration (HTTP ${configResponse.status}).`);
    }
    if (!mapboxResponse.ok) {
        throw new Error(`Unable to load Mapbox configuration from the transparent proxy (HTTP ${mapboxResponse.status}).`);
    }

    const config: Omit<RuntimeConfigurationModel, 'mapbox'> = await configResponse.json();
    const mapboxConfig: { accessToken?: unknown } | null = await mapboxResponse.json();
    const token = mapboxConfig?.accessToken;
    if (typeof token !== 'string' || !/^pk\.\S+$/.test(token.trim())) {
        throw new Error('The transparent proxy must supply a public Mapbox access token.');
    }

    return { ...config, mapbox: { accessToken: token.trim() } };
};
