import { Component, inject, Renderer2 } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogActions, MatDialogClose, MatDialogContent, MatDialogRef } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'downloadable-content-modal',
    imports: [MatButtonModule, MatDialogContent, MatDialogActions, MatDialogClose, MatIconModule],
    templateUrl: './downloadable-content-modal.html',
    styleUrl: './downloadable-content-modal.scss',
})
export class DownloadableContentModal {
    readonly #dialogRef = inject(MatDialogRef<DownloadableContentModal>);
    readonly #renderer = inject(Renderer2);
    readonly #pdfFilepath = '../../../assets/';

    public readonly data = inject<{ pdfFilename: string; content: string }>(MAT_DIALOG_DATA);
    public readonly pdfFilePathAndName = `${this.#pdfFilepath}${this.data.pdfFilename}`;

    public onDownload(): void {
        const downloadLink = this.#renderer.createElement('a');
        downloadLink.setAttribute('target', '_self');
        downloadLink.setAttribute('href', this.pdfFilePathAndName);
        downloadLink.setAttribute('download', this.data.pdfFilename);
        downloadLink.click();
        downloadLink.remove();
        this.#dialogRef.close();
    }
}
