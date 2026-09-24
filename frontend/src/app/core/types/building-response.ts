import { BuiltForm, EPCRating, StructureUnitType } from '@core/enums';

export type EPCBuildingResponseModel = {
    BuiltForm: BuiltForm;
    EPC: EPCRating;
    FullAddress: string;
    LodgementDate: string;
    InsulationTypes: string;
    InsulationThickness: string;
    InsulationThicknessLowerBound: string;
    ParentTOID?: string;
    PartTypes: string;
    PostCode: string;
    StructureUnitType: StructureUnitType;
    UPRN: string;
    TOID?: string;
};

export type NoEPCBuildingResponseModel = Omit<
    EPCBuildingResponseModel,
    'BuiltForm' | 'EPC' | 'LodgementDate' | 'InsulationTypes' | 'InsulationThickness' | 'InsulationThicknessLowerBound' | 'PartTypes' | 'StructureUnitType'
> & {
    latitude: string;
    longitude: string;
};

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2026. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the UK's Department for Business, Innovation, Science and Trade (BIST) as the governing entity.
