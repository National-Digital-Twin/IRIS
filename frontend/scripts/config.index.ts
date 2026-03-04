import { writeFile } from 'node:fs';

const env = process.env.ENV;

const production = env === 'prod';

const osAPIKey = process.env.OS_API_KEY;

const maptilerAPIKey = process.env.MAPTILER_API_KEY;

const targetPath = `./src/environments/environment.ts`;

const envConfigFile = `export const environment = {
        maptiler: {
            apiKey: '${maptilerAPIKey},
        },
        os: {
            apiKey: '${osAPIKey}',
        },
        production: ${production},
    };
`;

writeFile(targetPath, envConfigFile, 'utf8', (err) => {
    if (err) {
        return console.log(err);
    }
});
