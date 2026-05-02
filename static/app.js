/**
 * 敏感信息加密工具 - 前端逻辑
 */

// ─── State ──────────────────────────────────────────────────
const state = {
    currentMode: 'mask',
    scanResult: null,
    uploadName: null,
    unmaskFile: null,
    selectedMapping: null,
    maskedOutputFile: null,
    restoredOutputFile: null,
};

// ─── Type labels ────────────────────────────────────────────
const TYPE_NAMES = {
    ID_CARD: '身份证号',
    PHONE: '手机号',
    BANK_CARD: '银行卡号',
    EMAIL: '邮箱',
    TEL: '固定电话',
    AMOUNT: '金额',
    COMPANY: '公司名',
    ADDRESS: '地址',
    CUSTOM: '自定义',
};

const TYPE_ICONS = {
    ID_CARD: '🪪',
    PHONE: '📱',
    BANK_CARD: '💳',
    EMAIL: '📧',
    TEL: '☎️',
    AMOUNT: '💰',
    COMPANY: '🏢',
    ADDRESS: '📍',
    CUSTOM: '🏷️',
};

// ─── DOM refs ───────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ─── Mode switch ────────────────────────────────────────────
$$('.mode-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        switchMode(mode);
    });
});

function switchMode(mode) {
    state.currentMode = mode;
    $$('.mode-btn').forEach((b) => b.classList.toggle('active', b.dataset.mode === mode));
    $$('.panel').forEach((p) => p.classList.add('hidden'));
    $(`#panel-${mode}`).classList.remove('hidden');

    if (mode === 'unmask') loadMappings();
    if (mode === 'settings') {
        loadCustomWords();
        loadMappingsManage();
    }
}

// ─── Drop zone setup ────────────────────────────────────────
function setupDropZone(zoneId, fileInputId, onFile) {
    const zone = $(zoneId);
    const input = $(fileInputId);

    zone.addEventListener('click', (e) => {
        if (e.target.closest('.file-label') || e.target === zone || e.target.closest('.drop-content')) {
            input.click();
        }
    });

    input.addEventListener('change', () => {
        if (input.files.length) onFile(input.files[0]);
    });

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) onFile(e.dataTransfer.files[0]);
    });
}

// ─── Mask flow ──────────────────────────────────────────────
setupDropZone('#drop-mask', '#file-mask', handleMaskFile);

async function handleMaskFile(file) {
    // Reset
    $('#scan-result').classList.add('hidden');
    $('#mask-done').classList.add('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const resp = await fetch('/api/scan', { method: 'POST', body: formData });
        const data = await resp.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        state.scanResult = data;
        state.uploadName = data.upload_name;
        renderScanResult(data);
    } catch (e) {
        showToast('扫描失败: ' + e.message, 'error');
    }
}

function renderScanResult(data) {
    $('#scan-filename').textContent = data.filename;
    updateStats(data.items);

    // Items with checkbox and delete button
    const itemsHtml = data.items
        .map(
            (item, i) => `
        <div class="item-row" data-index="${i}">
            <input type="checkbox" class="item-check" data-index="${i}" checked>
            <span class="item-type">${TYPE_NAMES[item.type] || item.type}</span>
            <span class="item-value">${escapeHtml(item.value)}</span>
            <span class="item-arrow">→</span>
            <span class="item-placeholder">[${item.type}_${String(i + 1).padStart(3, '0')}]</span>
            <button class="item-del" data-index="${i}" title="移除此项">✕</button>
        </div>
    `
        )
        .join('');

    // Toolbar: select all / deselect all
    const toolbar = data.items.length > 0 ? `
        <div class="items-toolbar">
            <button class="btn-link" id="btn-check-all">全选</button>
            <span class="toolbar-sep">|</span>
            <button class="btn-link" id="btn-uncheck-all">取消全选</button>
            <span class="items-count"><span id="checked-count">${data.items.length}</span> / ${data.items.length} 项</span>
        </div>
    ` : '';

    $('#scan-items').innerHTML = toolbar + (itemsHtml || '<p class="empty-state">未检测到敏感信息</p>');

    // Bind checkbox events
    $$('.item-check').forEach((cb) => {
        cb.addEventListener('change', () => {
            const row = cb.closest('.item-row');
            row.classList.toggle('item-disabled', !cb.checked);
            updateCheckedCount();
        });
    });

    // Bind delete buttons
    $$('.item-del').forEach((btn) => {
        btn.addEventListener('click', () => {
            const row = btn.closest('.item-row');
            row.remove();
            updateCheckedCount();
        });
    });

    // Bind select all / deselect all
    if ($('#btn-check-all')) {
        $('#btn-check-all').addEventListener('click', () => {
            $$('.item-check').forEach((cb) => { cb.checked = true; cb.closest('.item-row').classList.remove('item-disabled'); });
            updateCheckedCount();
        });
        $('#btn-uncheck-all').addEventListener('click', () => {
            $$('.item-check').forEach((cb) => { cb.checked = false; cb.closest('.item-row').classList.add('item-disabled'); });
            updateCheckedCount();
        });
    }

    $('#scan-result').classList.remove('hidden');
}

function updateStats(items) {
    const by_type = {};
    items.forEach((item) => {
        by_type[item.type] = (by_type[item.type] || 0) + 1;
    });
    const statsHtml = Object.entries(by_type)
        .map(
            ([type, count]) => `
        <span class="stat-pill">
            ${TYPE_ICONS[type] || '📋'} ${TYPE_NAMES[type] || type}
            <span class="stat-count">${count}</span>
        </span>
    `
        )
        .join('');
    $('#scan-stats').innerHTML = statsHtml || '<span class="stat-pill">未检测到敏感信息</span>';
}

function updateCheckedCount() {
    const el = $('#checked-count');
    if (el) el.textContent = $$('.item-check:checked').length;
}

function getCheckedItems() {
    // 收集所有勾选的检测项
    const checked = [];
    $$('.item-row').forEach((row) => {
        const cb = row.querySelector('.item-check');
        if (cb && cb.checked) {
            const idx = parseInt(cb.dataset.index);
            if (state.scanResult && state.scanResult.items[idx]) {
                checked.push(state.scanResult.items[idx]);
            }
        }
    });
    return checked;
}

// Confirm mask - send only checked items
$('#btn-do-mask').addEventListener('click', async () => {
    const checkedItems = getCheckedItems();
    if (checkedItems.length === 0) {
        showToast('请至少选择一项需要脱敏的信息', 'error');
        return;
    }

    const btn = $('#btn-do-mask');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 处理中...';

    try {
        const resp = await fetch('/api/mask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ upload_name: state.uploadName, items: checkedItems, original_name: state.scanResult.filename }),
        });
        const data = await resp.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        state.maskedOutputFile = data.output_file;
        $('#done-info').textContent = `共脱敏 ${data.masked_count} 处敏感信息，映射表: ${data.mapping_file}`;
        $('#scan-result').classList.add('hidden');
        $('#mask-done').classList.remove('hidden');
        showToast('脱敏完成！', 'success');
    } catch (e) {
        showToast('脱敏失败: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🛡️ 确认脱敏</span>';
    }
});

$('#btn-cancel-mask').addEventListener('click', () => {
    $('#scan-result').classList.add('hidden');
});

$('#btn-download-masked').addEventListener('click', () => {
    if (state.maskedOutputFile) {
        window.location.href = `/api/download/${encodeURIComponent(state.maskedOutputFile)}`;
    }
});

$('#btn-new-mask').addEventListener('click', () => {
    $('#mask-done').classList.add('hidden');
    $('#file-mask').value = '';
    state.scanResult = null;
    state.uploadName = null;
});

// ─── Unmask flow ────────────────────────────────────────────
setupDropZone('#drop-unmask', '#file-unmask', handleUnmaskFile);

function handleUnmaskFile(file) {
    state.unmaskFile = file;
    $('#unmask-selected').textContent = `✅ ${file.name}`;
    $('#unmask-selected').classList.remove('hidden');
    checkUnmaskReady();
}

async function loadMappings() {
    try {
        const resp = await fetch('/api/mappings');
        const data = await resp.json();

        if (!data.length) {
            $('#mapping-list').innerHTML = '<p class="empty-state">暂无映射表</p>';
            return;
        }

        $('#mapping-list').innerHTML = data
            .map(
                (m) => `
            <label class="mapping-item" data-name="${m.filename}">
                <input type="radio" name="mapping" value="${m.filename}">
                <span class="mapping-name">${m.filename}</span>
                <span class="mapping-date">${formatTime(m.modified)}</span>
            </label>
        `
            )
            .join('');

        // Bind selection
        $$('.mapping-item input').forEach((radio) => {
            radio.addEventListener('change', () => {
                $$('.mapping-item').forEach((el) => el.classList.remove('selected'));
                radio.closest('.mapping-item').classList.add('selected');
                state.selectedMapping = radio.value;
                checkUnmaskReady();
            });
        });
    } catch (e) {
        $('#mapping-list').innerHTML = '<p class="loading">加载失败</p>';
    }
}

function checkUnmaskReady() {
    $('#btn-do-unmask').disabled = !(state.unmaskFile && state.selectedMapping);
}

$('#btn-do-unmask').addEventListener('click', async () => {
    const btn = $('#btn-do-unmask');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 还原中...';

    const formData = new FormData();
    formData.append('file', state.unmaskFile);
    formData.append('mapping', state.selectedMapping);

    try {
        const resp = await fetch('/api/unmask', { method: 'POST', body: formData });
        const data = await resp.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        state.restoredOutputFile = data.output_file;
        $('#unmask-done').classList.remove('hidden');
        showToast('还原完成！', 'success');
    } catch (e) {
        showToast('还原失败: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🔓 执行还原</span>';
    }
});

$('#btn-download-restored').addEventListener('click', () => {
    if (state.restoredOutputFile) {
        window.location.href = `/api/download/${encodeURIComponent(state.restoredOutputFile)}`;
    }
});

$('#btn-new-unmask').addEventListener('click', () => {
    $('#unmask-done').classList.add('hidden');
    $('#unmask-selected').classList.add('hidden');
    $('#file-unmask').value = '';
    state.unmaskFile = null;
    state.selectedMapping = null;
    $$('.mapping-item').forEach((el) => el.classList.remove('selected'));
    $$('.mapping-item input').forEach((r) => (r.checked = false));
    checkUnmaskReady();
});

// ─── Settings ───────────────────────────────────────────────
async function loadCustomWords() {
    try {
        const resp = await fetch('/api/custom-words');
        const words = await resp.json();
        $('#custom-words').value = words.join('\n');
    } catch (e) {
        console.error(e);
    }
}

$('#btn-save-words').addEventListener('click', async () => {
    const text = $('#custom-words').value;
    const words = text
        .split('\n')
        .map((w) => w.trim())
        .filter(Boolean);

    try {
        const resp = await fetch('/api/custom-words', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ words }),
        });
        const data = await resp.json();
        showToast(`已保存 ${data.count} 个敏感词`, 'success');
    } catch (e) {
        showToast('保存失败', 'error');
    }
});

async function loadMappingsManage() {
    try {
        const resp = await fetch('/api/mappings');
        const data = await resp.json();

        if (!data.length) {
            $('#mapping-manage-list').innerHTML = '<p class="empty-state">暂无映射表</p>';
            return;
        }

        $('#mapping-manage-list').innerHTML = data
            .map(
                (m) => `
            <div class="manage-item" data-name="${m.filename}">
                <span class="manage-name">${m.filename}</span>
                <span class="manage-date">${formatTime(m.modified)}</span>
                <button class="manage-del" title="删除" onclick="deleteMapping('${m.filename}')">🗑️</button>
            </div>
        `
            )
            .join('');
    } catch (e) {
        $('#mapping-manage-list').innerHTML = '<p class="loading">加载失败</p>';
    }
}

async function deleteMapping(filename) {
    if (!confirm(`确定删除映射表 ${filename}？\n删除后将无法还原对应的脱敏文件！`)) return;

    try {
        await fetch(`/api/mappings/${encodeURIComponent(filename)}`, { method: 'DELETE' });
        showToast('已删除', 'success');
        loadMappingsManage();
    } catch (e) {
        showToast('删除失败', 'error');
    }
}

// expose to onclick
window.deleteMapping = deleteMapping;

// ─── Utils ──────────────────────────────────────────────────
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatTime(ts) {
    const d = new Date(ts * 1000);
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function showToast(msg, type = 'success') {
    const el = $('#toast');
    el.textContent = msg;
    el.className = `toast toast-${type}`;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 3000);
}
