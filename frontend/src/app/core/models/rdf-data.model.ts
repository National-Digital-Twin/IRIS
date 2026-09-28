export interface TableRow {
    [key: string]: string;
}

export interface RDFObject {
    type: string;
    value: string;
}

export interface RDFData {
    [key: string]: RDFObject;
}

export interface SPARQLReturn {
    head: {
        vars: string[];
    };
    results: {
        bindings: RDFData[];
    };
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
