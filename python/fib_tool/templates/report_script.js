// Get current HTML timestamp
function getReportTimestamp() {
    var meta = document.getElementById('report-timestamp');
    if (meta) {
        return meta.getAttribute('content');
    }
    return 'legacy';
}

// Custom image upload functionality
function addImage(markerId) {
    document.getElementById('file-input-' + markerId).click();
}

function handleImageUpload(markerId, files) {
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file.type.startsWith('image/')) {
            var reader = new FileReader();
            reader.onload = (function(f) {
                return function(e) {
                    var base64 = e.target.result;
                    displayCustomImage(markerId, base64, f.name);
                    saveCustomImage(markerId, base64, f.name);
                };
            })(file);
            reader.readAsDataURL(file);
        }
    }
}

function displayCustomImage(markerId, base64, filename) {
    var container = document.getElementById('custom-images-' + markerId);
    var imageId = 'custom-img-' + markerId + '-' + Date.now();

    var imgDiv = document.createElement('div');
    imgDiv.className = 'custom-image';
    imgDiv.id = imageId;
    imgDiv.innerHTML =
        '<img src="' + base64 + '" alt="Custom image">' +
        '<button onclick="removeCustomImage(\'' + markerId + '\', \'' + imageId + '\')" class="remove-btn" title="删除此图片">×</button>';

    container.appendChild(imgDiv);

    // Attach Lightbox functionality
    var img = imgDiv.querySelector('img');
    img.addEventListener('click', function() {
        openLightbox(this.src);
    });
}

function saveCustomImage(markerId, base64, filename) {
    var timestamp = getReportTimestamp();
    var storageKey = 'fib-custom-images-' + timestamp + '-' + markerId;
    var images = JSON.parse(localStorage.getItem(storageKey) || '[]');

    images.push({
        id: 'custom-img-' + markerId + '-' + Date.now(),
        filename: filename,
        data: base64,
        timestamp: new Date().toISOString()
    });

    localStorage.setItem(storageKey, JSON.stringify(images));
    updateStorageInfo();
}

function loadCustomImages() {
    var timestamp = getReportTimestamp();
    if (!timestamp) {
        console.warn('No report timestamp found, skipping image load');
        return;
    }

    var sections = document.querySelectorAll('.screenshots');
    for (var i = 0; i < sections.length; i++) {
        var section = sections[i];
        var markerId = section.getAttribute('data-marker-id');
        if (markerId) {
            var storageKey = 'fib-custom-images-' + timestamp + '-' + markerId;
            var images = JSON.parse(localStorage.getItem(storageKey) || '[]');

            for (var j = 0; j < images.length; j++) {
                var img = images[j];
                displayCustomImage(markerId, img.data, img.filename);
            }
        }
    }
}

function removeCustomImage(markerId, imageId) {
    var element = document.getElementById(imageId);
    if (element) {
        element.remove();
    }

    var timestamp = getReportTimestamp();
    if (!timestamp) return;

    var storageKey = 'fib-custom-images-' + timestamp + '-' + markerId;
    var images = JSON.parse(localStorage.getItem(storageKey) || '[]');
    images = images.filter(function(img) {
        return img.id !== imageId;
    });
    localStorage.setItem(storageKey, JSON.stringify(images));

    updateStorageInfo();
}

function clearAllCustomImages() {
    if (!confirm('确定要清除当前报告的所有自定义图片吗？此操作不可撤销！')) {
        return;
    }

    var timestamp = getReportTimestamp();
    if (!timestamp) return;

    // Remove from DOM
    var customImages = document.querySelectorAll('.custom-image');
    for (var i = 0; i < customImages.length; i++) {
        customImages[i].remove();
    }

    // Clear localStorage for this report only
    var keys = Object.keys(localStorage);
    var prefix = 'fib-custom-images-' + timestamp + '-';
    for (var i = 0; i < keys.length; i++) {
        if (keys[i].startsWith(prefix)) {
            localStorage.removeItem(keys[i]);
        }
    }

    // Also clear notes for this report
    localStorage.removeItem('fib-notes-' + timestamp);

    updateStorageInfo();
    alert('当前报告的所有自定义图片已清除！');
}

function updateStorageInfo() {
    var timestamp = getReportTimestamp();
    if (!timestamp) return;

    var totalSize = 0;
    var keys = Object.keys(localStorage);
    var prefix = 'fib-custom-images-' + timestamp + '-';
    var notesKey = 'fib-notes-' + timestamp;
    
    for (var i = 0; i < keys.length; i++) {
        if (keys[i].startsWith(prefix) || keys[i] === notesKey) {
            totalSize += localStorage[keys[i]].length;
        }
    }

    var sizeKB = (totalSize / 1024).toFixed(2);
    var storageElement = document.getElementById('storage-used');
    if (storageElement) {
        storageElement.textContent = sizeKB + ' KB (当前报告)';
    }

    // Warning if approaching 5MB limit
    if (totalSize > 5 * 1024 * 1024 * 0.8) {
        alert('警告：当前报告存储空间接近限制（5MB），建议导出报告并清除部分图片。');
    }
}

function exportHTMLWithImages() {
    // Save notes to localStorage first
    saveNotes();
    
    // Sync textarea value to DOM
    var reportNotes = document.getElementById('report-notes');
    if (reportNotes) {
        reportNotes.setAttribute('value', reportNotes.value);
        reportNotes.textContent = reportNotes.value;
    }
    
    // Clone current document
    var clone = document.documentElement.cloneNode(true);

    // Remove export buttons and file inputs from clone
    var elementsToRemove = clone.querySelectorAll('.save-btn, .export-btn, .load-btn, .clear-btn, input[type="file"], .add-image-btn button');
    for (var i = 0; i < elementsToRemove.length; i++) {
        elementsToRemove[i].remove();
    }

    // Generate complete HTML
    var htmlContent = '<!DOCTYPE html>\n' + clone.outerHTML;

    // Trigger download
    var blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'FIB_Report_with_Custom_Images_' + getTimestamp() + '.html';
    a.click();
    URL.revokeObjectURL(url);

    alert('报告已导出！包含所有自定义图片和 Notes 的 HTML 文件已下载。');
}

function getTimestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

// Lightbox functionality
function openLightbox(imgSrc) {
    var lightbox = document.getElementById('lightbox');
    var lightboxImg = document.getElementById('lightbox-img');
    lightboxImg.src = imgSrc;
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    var lightbox = document.getElementById('lightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

// ESC key to close Lightbox
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeLightbox();
    }
});

// Attach lightbox to all images
function attachLightboxToImages() {
    var images = document.querySelectorAll('.screenshot img, .custom-image img');
    for (var i = 0; i < images.length; i++) {
        images[i].addEventListener('click', function(e) {
            if (e.target.className === 'remove-btn') {
                return;
            }
            openLightbox(this.src);
        });
    }
}

// Notes persistence
function saveNotes() {
    var timestamp = getReportTimestamp();
    if (!timestamp) {
        console.warn('No report timestamp found, cannot save notes');
        return false;
    }

    var reportNotes = document.getElementById('report-notes');
    if (reportNotes) {
        var storageKey = 'fib-notes-' + timestamp;
        localStorage.setItem(storageKey, reportNotes.value);
        updateStorageInfo();
        console.log('Notes saved successfully to:', storageKey);
        return true;
    } else {
        console.warn('Report notes textarea not found');
        return false;
    }
}

function loadNotes() {
    var timestamp = getReportTimestamp();
    if (!timestamp) {
        console.warn('No report timestamp found, skipping notes load');
        return;
    }

    var storageKey = 'fib-notes-' + timestamp;
    var savedNotes = localStorage.getItem(storageKey);
    
    if (savedNotes) {
        var reportNotes = document.getElementById('report-notes');
        if (reportNotes) {
            reportNotes.value = savedNotes;
            console.log('Notes loaded successfully from:', storageKey);
        }
    } else {
        console.log('No saved notes found for this report');
    }
}

// Auto-save notes (debounced)
var saveNotesTimeout;
function autoSaveNotes() {
    clearTimeout(saveNotesTimeout);
    saveNotesTimeout = setTimeout(saveNotes, 1000);
}

// Load custom images on page load
window.addEventListener('DOMContentLoaded', function() {
    loadCustomImages();
    loadNotes();
    updateStorageInfo();
    attachLightboxToImages();

    // Add auto-save listener to notes textarea
    var textareas = document.querySelectorAll('textarea[id^="notes-"]');
    for (var i = 0; i < textareas.length; i++) {
        textareas[i].addEventListener('input', autoSaveNotes);
    }
});
