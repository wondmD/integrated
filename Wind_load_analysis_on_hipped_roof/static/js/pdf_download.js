function downloadSection(sectionId, filename) {
    const element = document.getElementById(sectionId);
    if (!element) {
        console.error(`Element with ID ${sectionId} not found.`);
        return;
    }
    if (typeof html2pdf === 'undefined') {
        console.error('html2pdf.js is not loaded.');
        alert('Failed to generate PDF: html2pdf.js library is not available.');
        return;
    }
    const clone = element.cloneNode(true);
    clone.querySelectorAll('.no-print').forEach(el => el.style.display = 'none');
    document.body.appendChild(clone);
    html2pdf()
        .set({
            margin: 0.5,
            filename: filename,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
        })
        .from(clone)
        .save()
        .then(() => document.body.removeChild(clone))
        .catch(err => {
            console.error('Error generating PDF:', err);
            document.body.removeChild(clone);
        });
}