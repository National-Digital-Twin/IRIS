import { environment } from '@environment';
import { loadRuntimeConfiguration } from './runtime-configuration';

describe('runtime configuration', () => {
    const proxyUrl = environment.transparent_proxy.url;
    const responseFor = (value: unknown): { ok: boolean; status: number; json: jest.Mock } => ({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(value),
    });
    const fetchConfig = (config: unknown, mapboxConfig: unknown): jest.Mock =>
        jest.fn().mockResolvedValueOnce(responseFor(config)).mockResolvedValueOnce(responseFor(mapboxConfig));

    afterEach(() => {
        environment.transparent_proxy.url = proxyUrl;
    });

    it('uses the fresh proxy token instead of a stale application token and preserves map settings', async () => {
        const config = { mapbox: { accessToken: 'pk.stale-token' }, map: { zoom: 6 } };
        const request = fetchConfig(config, { accessToken: '  pk.test-public-token  ' });

        const result = await loadRuntimeConfiguration(request);

        expect(request).toHaveBeenCalledWith('configuration/config.json');
        expect(request).toHaveBeenCalledWith('/transparent-proxy/mapbox-config', { cache: 'no-store' });
        expect(result.mapbox.accessToken).toBe('pk.test-public-token');
        expect(result.map).toEqual(config.map);
    });

    it.each(['/transparent-proxy/', 'https://proxy.example/maps/', '/gateway/maps'])('uses the configured proxy base URL (%s)', async (url) => {
        environment.transparent_proxy.url = url;
        const request = fetchConfig({}, { accessToken: 'pk.test-public-token' });

        await loadRuntimeConfiguration(request);

        expect(request).toHaveBeenCalledWith(`${url.replace(/\/$/, '')}/mapbox-config`, { cache: 'no-store' });
    });

    it.each([undefined, null, '', ' ', 'undefined', 'null', 'sk.secret-token', 'pk.', 'pk.token with spaces', 123])(
        'rejects an invalid proxy token without falling back to application configuration (%s)',
        async (accessToken) => {
            const request = fetchConfig({ mapbox: { accessToken: 'pk.stale-token' } }, { accessToken });
            await expect(loadRuntimeConfiguration(request)).rejects.toThrow('public Mapbox access token');
        },
    );

    it.each([null, {}])('rejects a missing proxy token (%s)', async (mapboxConfig) => {
        await expect(loadRuntimeConfiguration(fetchConfig({}, mapboxConfig))).rejects.toThrow('public Mapbox access token');
    });

    it.each(['application', 'proxy'])('rejects a failed %s configuration request before parsing responses', async (source) => {
        const configResponse = responseFor({});
        const mapboxResponse = responseFor({ accessToken: 'pk.test-public-token' });
        Object.assign(source === 'application' ? configResponse : mapboxResponse, { ok: false, status: 503 });
        const request = jest.fn().mockResolvedValueOnce(configResponse).mockResolvedValueOnce(mapboxResponse);

        await expect(loadRuntimeConfiguration(request)).rejects.toThrow('HTTP 503');
        expect(configResponse.json).not.toHaveBeenCalled();
        expect(mapboxResponse.json).not.toHaveBeenCalled();
    });

    it('rejects an unreachable proxy', async () => {
        const request = jest.fn().mockResolvedValueOnce(responseFor({})).mockRejectedValueOnce(new Error('Proxy unavailable'));
        await expect(loadRuntimeConfiguration(request)).rejects.toThrow('Proxy unavailable');
    });

    it('rejects a malformed proxy response', async () => {
        const mapboxResponse = responseFor(null);
        mapboxResponse.json.mockRejectedValue(new SyntaxError('Invalid proxy JSON'));
        const request = jest.fn().mockResolvedValueOnce(responseFor({})).mockResolvedValueOnce(mapboxResponse);
        await expect(loadRuntimeConfiguration(request)).rejects.toThrow('Invalid proxy JSON');
    });
});
