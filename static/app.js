/* =============================================================
   NANDALIN PRO — Lógica do Aplicativo
   ============================================================= */

// ============ ESTADO GLOBAL ============
const App = {
    arquivo: null,        // nome do arquivo enviado
    infoVideo: null,       // informações do vídeo
    analise: null,         // resultado da análise IA
    config: {},            // configuração de processamento
    jobId: null,           // ID do job de processamento
    presets: {},           // presets disponíveis
    presetSelecionado: null,
};

const E = (id) => document.getElementById(id);

// ============ TOASTS ============
function showToast(mensagem, tipo = 'info', duracao = 4000) {
    const container = E('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.textContent = mensagem;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, duracao);
}

// ============ HEALTH CHECK ============
async function checkHealth() {
    try {
        const res = await fetch('/api/health');
        const data = await res.json();
        const statusEl = E('healthStatus');
        const dot = statusEl.querySelector('.status-dot');

        if (data.ffmpeg && data.ffprobe) {
            dot.className = 'status-dot online';
            statusEl.querySelector('span:last-child').textContent =
                `FFmpeg ✓ | OpenCV ${data.opencv ? '✓' : '✗'}`;
        } else {
            dot.className = 'status-dot offline';
            statusEl.querySelector('span:last-child').textContent = 'FFmpeg não encontrado!';
        }
    } catch (e) {
        E('healthStatus').querySelector('span:last-child').textContent = 'Servidor offline';
    }
}

// ============ UPLOAD ============
const uploadZone = E('uploadZone');
const fileInput = E('fileInput');

uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        uploadFile(e.dataTransfer.files[0]);
    }
});
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        uploadFile(e.target.files[0]);
    }
});

async function uploadFile(file) {
    if (!file.type.startsWith('video/')) {
        showToast('⚠️ Por favor selecione um arquivo de vídeo!', 'warning');
        return;
    }

    // Mostrar progresso
    E('uploadProgress').style.display = 'block';
    uploadZone.style.display = 'none';
    E('uploadProgressText').textContent = `Enviando ${file.name}...`;
    E('uploadProgressFill').style.width = '0%';

    const formData = new FormData();
    formData.append('video', file);

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/upload');

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                E('uploadProgressFill').style.width = `${pct}%`;
                E('uploadProgressText').textContent =
                    `Enviando... ${pct}% (${formatSize(e.loaded)})`;
            }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                if (data.sucesso) {
                    App.arquivo = data.arquivo;
                    App.infoVideo = data.info;
                    E('uploadProgressFill').style.width = '100%';
                    E('uploadProgressText').textContent = '✅ Vídeo enviado!';
                    showToast('✅ Vídeo carregado com sucesso!', 'success');
                    setTimeout(setupAfterUpload, 600);
                } else {
                    showToast(`❌ ${data.erro}`, 'error');
                    resetUpload();
                }
            } else {
                showToast(`❌ Erro no upload (${xhr.status})`, 'error');
                resetUpload();
            }
        };

        xhr.onerror = () => {
            showToast('❌ Erro de conexão no upload', 'error');
            resetUpload();
        };

        xhr.send(formData);
    } catch (e) {
        showToast(`❌ Erro: ${e.message}`, 'error');
        resetUpload();
    }
}

function resetUpload() {
    E('uploadProgress').style.display = 'none';
    uploadZone.style.display = 'block';
}

function formatSize(bytes) {
    if (bytes > 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
    if (bytes > 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
    return `${(bytes / 1024).toFixed(1)} KB`;
}

// ============ APÓS UPLOAD ============
function setupAfterUpload() {
    resetUpload();
    E('stepUpload').style.display = 'none';
    E('stepInfo').style.display = 'block';

    // Mostrar preview
    const preview = E('videoPreview');
    preview.src = `/api/video/uploads/${App.arquivo}`;
    E('videoPreviewContainer').style.display = 'block';

    // Info overlay
    const info = App.infoVideo;
    E('videoInfoOverlay').innerHTML = `
        <span class="info-item">📐 ${info.resolucao}</span>
        <span class="info-item">📊 ${info.megapixels} MP</span>
        <span class="info-item">⏱️ ${info.duracao_formatada}</span>
        <span class="info-item">📱 ${info.orientacao}</span>
    `;

    // Mostrar botão analisar
    E('analyzeSection').style.display = 'block';
    E('btnAnalyze').disabled = false;

    showToast('📹 Vídeo pronto! Clique em "Analisar com IA"', 'info');
}

// ============ ANÁLISE IA ============
async function startAnalysis() {
    const btn = E('btnAnalyze');
    btn.disabled = true;
    btn.textContent = '🧠 Analisando vídeo... aguarde';

    showToast('🧠 IA analisando o vídeo... (pode levar alguns segundos)', 'info');

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ arquivo: App.arquivo }),
        });

        const data = await res.json();

        if (data.sucesso) {
            App.analise = data.analise;
            renderAnalysis(data.analise);
            btn.textContent = '✅ Análise concluída!';
            showToast('✅ Análise concluída! Veja as recomendações da IA.', 'success');
        } else {
            btn.textContent = '🧠 Analisar com IA';
            btn.disabled = false;
            showToast(`❌ ${data.erro}`, 'error');
        }
    } catch (e) {
        btn.textContent = '🧠 Analisar com IA';
        btn.disabled = false;
        showToast('❌ Erro ao analisar: ' + e.message, 'error');
    }
}

function renderAnalysis(analise) {
    E('analysisResults').style.display = 'block';

    const qualidade = analise.analise_qualidade;
    const info = analise.info_basica;

    // Cards de qualidade
    const cards = [];
    if (qualidade && Object.keys(qualidade).length > 0) {
        cards.push(cardHTML('🎞️', 'Score de Qualidade', qualidade.score_geral, true));
        cards.push(cardHTML('🔍', 'Nitidez', qualidade.nitidez_classe,
            false, qualidade.nitidez_classe));
        cards.push(cardHTML('🔆', 'Contraste', qualidade.contraste_classe,
            false, qualidade.contraste_classe));
        cards.push(cardHTML('✂️', 'Cenas Detectadas', `${qualidade.total_cenas}`));
        cards.push(cardHTML('🎥', 'Resolução', info.resolucao));
        cards.push(cardHTML('📊', 'Resolução', `${info.megapixels} MP`));
    } else {
        cards.push(cardHTML('🎥', 'Resolução', info.resolucao));
        cards.push(cardHTML('📊', 'Megapixels', `${info.megapixels} MP`));
        cards.push(cardHTML('⏱️', 'Duração', info.duracao_formatada));
        cards.push(cardHTML('📱', 'Orientação', info.orientacao));
    }
    E('qualityCards').innerHTML = cards.join('');

    // Recomendações da IA
    const recos = analise.recomendacoes || [];
    if (recos.length > 0) {
        const recoHTML = recos.map(reco => `
            <div class="reco-card">
                <div class="reco-icon">${reco.icone}</div>
                <div class="reco-content">
                    <h4>${reco.titulo}</h4>
                    <p>${reco.texto}</p>
                </div>
            </div>
        `).join('');
        E('recommendations').innerHTML = `
            <h3>🧠 Recomendações da IA</h3>
            ${recoHTML}
        `;
    }

    // Melhores momentos
    const momentos = analise.melhores_momentos || [];
    if (momentos.length > 0) {
        E('bestMoments').style.display = 'block';
        E('momentsList').innerHTML = momentos.map((m, i) => `
            <div class="moment-item">
                <div class="time">#${i + 1} — ⏱️ ${m.tempo}s</div>
                <div>Score: ${m.score}</div>
                <div>Nitidez: ${m.nitidez}</div>
            </div>
        `).join('');
    }

    // Mostrar step 3
    E('btnAnalyze').textContent = '🧠 Analisar com IA';
    E('btnAnalyze').disabled = true;

    setTimeout(() => {
        E('stepConfig').style.display = 'block';
        loadPresets();
        E('stepConfig').scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

function cardHTML(icone, label, valor, gradient = false, badge = null) {
    let badgeHTML = '';
    if (badge) {
        const cls = badge === 'Alta' || badge === 'Alto' ? 'badge-high'
                  : badge === 'Média' || badge === 'Médio' ? 'badge-med'
                  : 'badge-low';
        badgeHTML = `<div class="card-badge ${cls}">${badge}</div>`;
    }
    return `
        <div class="quality-card">
            <div class="card-icon">${icone}</div>
            <div class="card-label">${label}</div>
            <div class="card-value ${gradient ? 'highlight' : ''}">${valor}</div>
            ${badgeHTML}
        </div>
    `;
}

// ============ PRESETS ============
async function loadPresets() {
    try {
        const res = await fetch('/api/presets');
        App.presets = await res.json();

        const grid = E('presetsGrid');
        grid.innerHTML = Object.entries(App.presets).map(([key, preset]) => `
            <button class="btn-preset" data-preset="${key}" onclick="selectPreset('${key}')">
                <h4>${preset.nome}</h4>
                <p>${preset.descricao}</p>
            </button>
        `).join('');

        // Selecionar o primeiro preset por padrão
        selectPreset('cinematico_4k');
    } catch (e) {
        showToast('❌ Erro ao carregar presets', 'error');
    }
}

function selectPreset(key) {
    App.presetSelecionado = key;
    const preset = App.presets[key];
    if (!preset) return;

    // Atualizar UI de seleção
    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.preset === key);
    });

    App.config = { ...preset.config };
    applyConfigToUI();

    E('stepProcess').style.display = 'block';
    renderSummary();
}

// ============ APLICAR CONFIG À UI ============
function applyConfigToUI() {
    const c = App.config;

    setSelect('cfgResolucao', c.resolucao);
    setSelect('cfgModo', c.modo);
    setSelect('cfgCodec', c.codec);
    setSelect('cfgFps', String(c.fps || 60));

    setRange('cfgCrf', c.crf ?? 18, (v) => `${v}`, (v) => `Crf ${v}`);
    setRange('cfgBrightness', Math.round((c.brightness ?? 0.03) * 100), (v) => `${v > 0 ? '+' : ''}${v}%`);
    setRange('cfgContrast', Math.round((c.contrast ?? 1.25) * 100), (v) => `+${v - 100}%`);
    setRange('cfgSaturation', Math.round((c.saturation ?? 1.5) * 100), (v) => `+${v - 100}%`);
    setRange('cfgGamma', Math.round((c.gamma ?? 0.95) * 100), (v) => (v / 100).toFixed(2));
    setRange('cfgTemperature', c.temperature ?? 5500, (v) => `${v}K`);
    setRange('cfgDenoiseForce', c.denoise_force ?? 4, (v) => v);

    setCheckbox('cfgDenoise', c.denoise ?? true);
    setCheckbox('cfgSharpen', c.sharpen ?? true);
    setCheckbox('cfgSharpenPost', c.sharpen_post ?? true);
    setCheckbox('cfgColorBalance', c.color_balance ?? true);
    setCheckbox('cfgVignette', c.vignette ?? false);

    setSelect('cfgCurves', c.curves || 'none');
}

function setSelect(id, value) {
    const el = E(id);
    if (el && el.value !== String(value)) {
        el.value = String(value);
    }
}

function setCheckbox(id, checked) {
    const el = E(id);
    if (el) el.checked = !!checked;
}

function setRange(id, value, fmt) {
    const el = E(id);
    if (!el) return;
    el.value = String(value);
    const valEl = E(id + 'Val');
    if (valEl) valEl.textContent = fmt(value);
}

// ============ EVENT LISTENERS PARA CONTROLES ============
E('cfgResolucao').addEventListener('change', () => {
    App.config.resolucao = E('cfgResolucao').value;
    App.presetSelecionado = null;
    clearPresetSelection();
    renderSummary();
});
E('cfgModo').addEventListener('change', () => {
    App.config.modo = E('cfgModo').value;
    App.presetSelecionado = null;
    clearPresetSelection();
    renderSummary();
});
E('cfgCodec').addEventListener('change', () => {
    App.config.codec = E('cfgCodec').value;
    App.presetSelecionado = null;
    clearPresetSelection();
    renderSummary();
});
E('cfgFps').addEventListener('change', () => {
    App.config.fps = Number(E('cfgFps').value);
    App.presetSelecionado = null;
    clearPresetSelection();
    renderSummary();
});
E('cfgCurves').addEventListener('change', () => {
    App.config.curves = E('cfgCurves').value;
    App.presetSelecionado = null;
    clearPresetSelection();
});

// Ranges
E('cfgCrf').addEventListener('input', () => {
    const v = Number(E('cfgCrf').value);
    E('cfgCrfVal').textContent = v;
    App.config.crf = v;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgBrightness').addEventListener('input', () => {
    const v = Number(E('cfgBrightness').value);
    E('cfgBrightnessVal').textContent = `${v > 0 ? '+' : ''}${v}%`;
    App.config.brightness = v / 100;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgContrast').addEventListener('input', () => {
    const v = Number(E('cfgContrast').value);
    E('cfgContrastVal').textContent = `+${v - 100}%`;
    App.config.contrast = v / 100;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgSaturation').addEventListener('input', () => {
    const v = Number(E('cfgSaturation').value);
    E('cfgSaturationVal').textContent = `+${v - 100}%`;
    App.config.saturation = v / 100;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgGamma').addEventListener('input', () => {
    const v = Number(E('cfgGamma').value);
    E('cfgGammaVal').textContent = (v / 100).toFixed(2);
    App.config.gamma = v / 100;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgTemperature').addEventListener('input', () => {
    const v = Number(E('cfgTemperature').value);
    E('cfgTemperatureVal').textContent = `${v}K`;
    App.config.temperature = v;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgDenoiseForce').addEventListener('input', () => {
    const v = Number(E('cfgDenoiseForce').value);
    E('cfgDenoiseForceVal').textContent = v;
    App.config.denoise_force = v;
    App.presetSelecionado = null;
    clearPresetSelection();
});

// Checkboxes
E('cfgDenoise').addEventListener('change', () => {
    App.config.denoise = E('cfgDenoise').checked;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgSharpen').addEventListener('change', () => {
    App.config.sharpen = E('cfgSharpen').checked;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgSharpenPost').addEventListener('change', () => {
    App.config.sharpen_post = E('cfgSharpenPost').checked;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgColorBalance').addEventListener('change', () => {
    App.config.color_balance = E('cfgColorBalance').checked;
    App.presetSelecionado = null;
    clearPresetSelection();
});
E('cfgVignette').addEventListener('change', () => {
    App.config.vignette = E('cfgVignette').checked;
    App.presetSelecionado = null;
    clearPresetSelection();
});

function clearPresetSelection() {
    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.classList.remove('active');
    });
}

// ============ RESUMO ============
function renderSummary() {
    const c = App.config;
    const info = App.infoVideo;
    if (!c || !info) return;

    const resLabels = { '2k': '2K (2560×1440)', '4k': '4K (3840×2160)', '8k': '8K (7680×4320)' };
    const modoLabels = { 'original': 'Original (16:9)', 'story': 'Story (9:16)' };
    const codecLabels = { 'libx265': 'HEVC 10-bit', 'libx264': 'AVC (H.264)' };

    E('summaryPanel').innerHTML = `
        <h3>📋 Resumo da Configuração</h3>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="label">Resolução</div>
                <div class="value gradient">${resLabels[c.resolucao] || c.resolucao}</div>
            </div>
            <div class="summary-item">
                <div class="label">Modo</div>
                <div class="value">${modoLabels[c.modo] || c.modo}</div>
            </div>
            <div class="summary-item">
                <div class="label">Codec</div>
                <div class="value">${codecLabels[c.codec] || c.codec}</div>
            </div>
            <div class="summary-item">
                <div class="label">Qualidade</div>
                <div class="value" id="summaryCrf">CRF ${c.crf}</div>
            </div>
            <div class="summary-item">
                <div class="label">FPS</div>
                <div class="value">${c.fps}</div>
            </div>
            <div class="summary-item">
                <div class="label">Original</div>
                <div class="value">${info.resolucao} (${info.megapixels} MP)</div>
            </div>
        </div>
    `;
}

// ============ PROCESSAMENTO ============
async function startProcessing() {
    // Recoletar todos os valores da UI
    collectConfigFromUI();

    const btn = E('btnProcess');
    btn.disabled = true;
    btn.textContent = '⏳ Iniciando...';

    try {
        const res = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                arquivo: App.arquivo,
                config: App.config,
            }),
        });

        const data = await res.json();

        if (data.sucesso) {
            App.jobId = data.job_id;

            // Mostrar aba de progresso
            E('processActions').style.display = 'none';
            E('processingStatus').style.display = 'block';
            E('btnDownload').style.display = 'none';

            showToast('🚀 Processamento iniciado!', 'success');
            pollStatus();
        } else {
            btn.disabled = false;
            btn.textContent = '🚀 Iniciar Processamento';
            showToast(`❌ ${data.erro}`, 'error');
        }
    } catch (e) {
        btn.disabled = false;
        btn.textContent = '🚀 Iniciar Processamento';
        showToast('❌ Erro ao iniciar: ' + e.message, 'error');
    }
}

function collectConfigFromUI() {
    App.config = {
        resolucao: E('cfgResolucao').value,
        modo: E('cfgModo').value,
        codec: E('cfgCodec').value,
        crf: Number(E('cfgCrf').value),
        fps: Number(E('cfgFps').value),
        brightness: Number(E('cfgBrightness').value) / 100,
        contrast: Number(E('cfgContrast').value) / 100,
        saturation: Number(E('cfgSaturation').value) / 100,
        gamma: Number(E('cfgGamma').value) / 100,
        temperature: Number(E('cfgTemperature').value),
        denoise: E('cfgDenoise').checked,
        denoise_force: Number(E('cfgDenoiseForce').value),
        sharpen: E('cfgSharpen').checked,
        sharpen_post: E('cfgSharpenPost').checked,
        color_balance: E('cfgColorBalance').checked,
        vignette: E('cfgVignette').checked,
        curves: E('cfgCurves').value,
    };
}

// ============ POLLING DE STATUS ============
let pollInterval = null;

async function pollStatus() {
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/status/${App.jobId}`);
            const job = await res.json();

            if (job.status === 'processando' || job.status === 'iniciando') {
                const pct = job.progresso || 0;
                E('processProgressFill').style.width = `${pct}%`;
                E('processProgressText').textContent = `${pct}%`;
                E('processMessage').textContent = job.mensagem || 'Processando...';

                if (job.comando) {
                    E('processMessage').title = job.comando;
                }
            } else if (job.status === 'concluido') {
                clearInterval(pollInterval);
                renderResult(job.resultado);
            } else if (job.status === 'erro') {
                clearInterval(pollInterval);
                E('processingStatus').style.display = 'none';
                E('processActions').style.display = 'block';
                E('btnProcess').disabled = false;
                E('btnProcess').textContent = '🚀 Iniciar Processamento';
                showToast(`❌ ${job.mensagem}`, 'error');
            }
        } catch (e) {
            console.error('Erro ao verificar status:', e);
        }
    }, 2000);
}

// ============ RESULTADO ============
function renderResult(resultado) {
    E('processingStatus').style.display = 'none';

    const btnDownload = E('btnDownload');
    btnDownload.href = `/api/download/${resultado.arquivo_saida}`;
    btnDownload.style.display = 'inline-block';
    btnDownload.setAttribute('download', resultado.arquivo_saida);

    E('resultDetails').innerHTML = `
        <div class="summary-item">
            <div class="label">Resolução</div>
            <div class="value gradient">${resultado.resolucao}</div>
        </div>
        <div class="summary-item">
            <div class="label">Tamanho</div>
            <div class="value">${resultado.tamanho_mb} MB</div>
        </div>
        <div class="summary-item">
            <div class="label">Codec</div>
            <div class="value">${resultado.codec.toUpperCase()}</div>
        </div>
        <div class="summary-item">
            <div class="label">Qualidade</div>
            <div class="value">CRF ${resultado.crf}</div>
        </div>
        <div class="summary-item">
            <div class="label">FPS</div>
            <div class="value">${resultado.fps}</div>
        </div>
    `;

    E('resultPanel').style.display = 'block';
    E('resultPanel').scrollIntoView({ behavior: 'smooth' });

    showToast('🎉 Vídeo processado com sucesso!', 'success');

    // Adicionar player de comparação
    const preview = E('videoPreview');
    preview.src = `/api/video/processed/${resultado.arquivo_saida}`;
}

// ============ RESET ============
function resetAll() {
    // Recarregar a página para começar de novo
    window.location.reload();
}

// ============ INIT ============
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
});