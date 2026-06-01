// F1 Race Management System — client-side utilities
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 3 seconds
    document.querySelectorAll('.alert').forEach(el => {
        setTimeout(() => { const bs = bootstrap.Alert.getInstance(el); if (bs) bs.close(); }, 3000);
    });
});
