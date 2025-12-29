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
    
    // Also clear schematic images
    clearSchematicImages();

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
    var schematicKey = 'fib-schematic-images-' + timestamp;
    
    for (var i = 0; i < keys.length; i++) {
        if (keys[i].startsWith(prefix) || keys[i] === notesKey || keys[i] === schematicKey) {
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
    
    // Sync schematic caption inputs to DOM
    var captionInputs = document.querySelectorAll('.schematic-image-item .caption-input');
    for (var i = 0; i < captionInputs.length; i++) {
        captionInputs[i].setAttribute('value', captionInputs[i].value);
    }
    
    // Make sure schematic section is visible in export if it has content
    var schematicSection = document.getElementById('schematic-section');
    var schematicContainer = document.getElementById('schematic-images-container');
    var hadSchematicContent = schematicContainer && schematicContainer.children.length > 0;
    
    // Clone current document
    var clone = document.documentElement.cloneNode(true);

    // Remove export buttons and file inputs from clone
    var elementsToRemove = clone.querySelectorAll('.save-btn, .export-btn, .load-btn, .clear-btn, input[type="file"], .add-image-btn button, .schematic-add-btn, .schematic-controls');
    for (var i = 0; i < elementsToRemove.length; i++) {
        elementsToRemove[i].remove();
    }
    
    // Remove remove buttons from schematic images
    var schematicRemoveBtns = clone.querySelectorAll('.schematic-image-item .remove-btn');
    for (var i = 0; i < schematicRemoveBtns.length; i++) {
        schematicRemoveBtns[i].remove();
    }
    
    // Make schematic section visible in export if it has content
    var clonedSchematicSection = clone.querySelector('#schematic-section');
    if (clonedSchematicSection && hadSchematicContent) {
        clonedSchematicSection.style.display = 'block';
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

// ==================== Schematic Changes Section ====================

var MAX_SCHEMATIC_IMAGES = 10;

function toggleSchematicSection() {
    var section = document.getElementById('schematic-section');
    var btn = document.getElementById('schematic-toggle-btn');
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        btn.classList.add('expanded');
        btn.innerHTML = '📋 Hide Schematic Changes';
    } else {
        section.style.display = 'none';
        btn.classList.remove('expanded');
        btn.innerHTML = '📋 Add Schematic Changes';
    }
}

function handleSchematicImageUpload(files) {
    var currentCount = getSchematicImageCount();
    var remaining = MAX_SCHEMATIC_IMAGES - currentCount;
    
    if (remaining <= 0) {
        alert('已达到最大图片数量限制 (10张)');
        return;
    }
    
    var filesToProcess = Math.min(files.length, remaining);
    
    for (var i = 0; i < filesToProcess; i++) {
        var file = files[i];
        if (file.type.startsWith('image/')) {
            var reader = new FileReader();
            reader.onload = (function(f) {
                return function(e) {
                    var base64 = e.target.result;
                    var imageId = 'schematic-img-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                    displaySchematicImage(imageId, base64, f.name, '');
                    saveSchematicImage(imageId, base64, f.name, '');
                    updateSchematicCount();
                    updateSchematicAddButton();
                };
            })(file);
            reader.readAsDataURL(file);
        }
    }
    
    // Clear file input
    document.getElementById('schematic-file-input').value = '';
    
    if (files.length > filesToProcess) {
        alert('只添加了 ' + filesToProcess + ' 张图片，已达到最大限制 (10张)');
    }
}

function displaySchematicImage(imageId, base64, filename, caption) {
    var container = document.getElementById('schematic-images-container');
    
    var itemDiv = document.createElement('div');
    itemDiv.className = 'schematic-image-item';
    itemDiv.id = imageId;
    itemDiv.innerHTML =
        '<img src="' + base64 + '" alt="Schematic image" onclick="openLightbox(this.src)">' +
        '<button onclick="removeSchematicImage(\'' + imageId + '\')" class="remove-btn" title="删除此图片">x</button>' +
        '<input type="text" class="caption-input" placeholder="输入图片说明..." value="' + escapeHtml(caption) + '" onchange="updateSchematicCaption(\'' + imageId + '\', this.value)">';
    
    container.appendChild(itemDiv);
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/"/g, '&quot;');
}

function saveSchematicImage(imageId, base64, filename, caption) {
    var timestamp = getReportTimestamp();
    var storageKey = 'fib-schematic-images-' + timestamp;
    var images = JSON.parse(localStorage.getItem(storageKey) || '[]');
    
    images.push({
        id: imageId,
        filename: filename,
        data: base64,
        caption: caption,
        timestamp: new Date().toISOString()
    });
    
    localStorage.setItem(storageKey, JSON.stringify(images));
    updateStorageInfo();
}

function updateSchematicCaption(imageId, caption) {
    var timestamp = getReportTimestamp();
    var storageKey = 'fib-schematic-images-' + timestamp;
    var images = JSON.parse(localStorage.getItem(storageKey) || '[]');
    
    for (var i = 0; i < images.length; i++) {
        if (images[i].id === imageId) {
            images[i].caption = caption;
            break;
        }
    }
    
    localStorage.setItem(storageKey, JSON.stringify(images));
}

function removeSchematicImage(imageId) {
    var element = document.getElementById(imageId);
    if (element) {
        element.remove();
    }
    
    var timestamp = getReportTimestamp();
    if (!timestamp) return;
    
    var storageKey = 'fib-schematic-images-' + timestamp;
    var images = JSON.parse(localStorage.getItem(storageKey) || '[]');
    images = images.filter(function(img) {
        return img.id !== imageId;
    });
    localStorage.setItem(storageKey, JSON.stringify(images));
    
    updateSchematicCount();
    updateSchematicAddButton();
    updateStorageInfo();
}

function loadSchematicChanges() {
    var timestamp = getReportTimestamp();
    if (!timestamp) {
        console.warn('No report timestamp found, skipping schematic load');
        return;
    }
    
    var storageKey = 'fib-schematic-images-' + timestamp;
    var images = JSON.parse(localStorage.getItem(storageKey) || '[]');
    
    if (images.length > 0) {
        // Auto-expand section if there are saved images
        var section = document.getElementById('schematic-section');
        var btn = document.getElementById('schematic-toggle-btn');
        section.style.display = 'block';
        btn.classList.add('expanded');
        btn.innerHTML = '📋 Hide Schematic Changes';
        
        for (var i = 0; i < images.length; i++) {
            var img = images[i];
            displaySchematicImage(img.id, img.data, img.filename, img.caption || '');
        }
    }
    
    updateSchematicCount();
    updateSchematicAddButton();
}

function getSchematicImageCount() {
    var container = document.getElementById('schematic-images-container');
    return container ? container.children.length : 0;
}

function updateSchematicCount() {
    var count = getSchematicImageCount();
    var countElement = document.getElementById('schematic-image-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

function updateSchematicAddButton() {
    var count = getSchematicImageCount();
    var addButton = document.getElementById('schematic-add-button');
    
    if (addButton) {
        if (count >= MAX_SCHEMATIC_IMAGES) {
            addButton.disabled = true;
            addButton.innerHTML = '<span>已达到最大图片数量 (10张)</span>';
        } else {
            addButton.disabled = false;
            addButton.innerHTML = 
                '<span class="plus-icon">+</span>' +
                '<span>添加原理图图片</span>' +
                '<span class="hint">支持 PNG, JPG, GIF (最多10张)</span>';
        }
    }
}

function clearSchematicImages() {
    var timestamp = getReportTimestamp();
    if (!timestamp) return;
    
    // Remove from DOM
    var container = document.getElementById('schematic-images-container');
    if (container) {
        container.innerHTML = '';
    }
    
    // Clear localStorage
    var storageKey = 'fib-schematic-images-' + timestamp;
    localStorage.removeItem(storageKey);
    
    updateSchematicCount();
    updateSchematicAddButton();
    updateStorageInfo();
}

// ==================== End Schematic Changes Section ====================

// Load custom images on page load
window.addEventListener('DOMContentLoaded', function() {
    loadCustomImages();
    loadNotes();
    loadSchematicChanges();
    updateStorageInfo();
    attachLightboxToImages();

    // Add auto-save listener to notes textarea
    var textareas = document.querySelectorAll('textarea[id^="notes-"]');
    for (var i = 0; i < textareas.length; i++) {
        textareas[i].addEventListener('input', autoSaveNotes);
    }
});
