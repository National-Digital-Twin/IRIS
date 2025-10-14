import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { ChartService } from '../../chart.service';

@Component({
    selector: 'c477-region-selector',
    imports: [CommonModule, MatFormFieldModule, MatSelectModule],
    template: `
        <mat-form-field appearance="outline" class="inline-select">
            <mat-select multiple [value]="selectedRegions" (selectionChange)="onSelectionChange($event.value)">
                <mat-select-trigger>region</mat-select-trigger>
                @for (region of allRegions; track region) {
                    <mat-option [value]="region" [disabled]="selectedRegions.length === 1 && selectedRegions.includes(region)">
                        {{ region }}
                    </mat-option>
                }
            </mat-select>
        </mat-form-field>
    `,
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RegionSelectorComponent {
    @Input() public selectedRegions: string[] = [];
    @Output() public selectedRegionsChange = new EventEmitter<string[]>();

    readonly #chartService = inject(ChartService);

    public get allRegions(): string[] {
        return this.#chartService.allRegions;
    }

    public onSelectionChange(regions: string[]): void {
        this.selectedRegionsChange.emit(regions);
    }
}

// SPDX-License-Identifier: Apache-2.0
// © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
// and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
