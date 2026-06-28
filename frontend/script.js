const API_BASE = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    const recordSelect = document.getElementById('record-select');
    const durationSlider = document.getElementById('duration-slider');
    const durationVal = document.getElementById('duration-val');
    const processBtn = document.getElementById('process-btn');
    const loading = document.getElementById('loading');
    const bpmDisplay = document.getElementById('bpm-display');
    const bpmStatus = document.getElementById('bpm-status');
    const accuracyDisplay = document.getElementById('accuracy-display');

    // Update slider value text
    durationSlider.addEventListener('input', (e) => {
        durationVal.textContent = e.target.value;
    });

    // Fetch available records on load
    fetch(`${API_BASE}/records`)
        .then(res => res.json())
        .then(data => {
            recordSelect.innerHTML = '';
            if(data.records && data.records.length > 0) {
                data.records.forEach(rec => {
                    const option = document.createElement('option');
                    option.value = rec;
                    option.textContent = `Registro ${rec}`;
                    recordSelect.appendChild(option);
                });
                // Carregar o primeiro automaticamente
                processSignal();
            } else {
                recordSelect.innerHTML = '<option value="">Nenhum registro encontrado</option>';
            }
        })
        .catch(err => {
            console.error('Erro ao buscar registros:', err);
            recordSelect.innerHTML = '<option value="">Erro de conexão</option>';
        });

    processBtn.addEventListener('click', processSignal);

    function processSignal() {
        const record = recordSelect.value;
        const duration = durationSlider.value;
        
        if (!record) return;

        processBtn.disabled = true;
        loading.style.display = 'flex';

        fetch(`${API_BASE}/process?record=${record}&duration=${duration}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert('Erro no processamento: ' + data.error);
                    return;
                }
                updateDashboard(data);
            })
            .catch(err => {
                console.error(err);
                alert('Erro ao processar. O backend está rodando?');
            })
            .finally(() => {
                processBtn.disabled = false;
                loading.style.display = 'none';
            });
    }

    function updateDashboard(data) {
        // Update BPM
        bpmDisplay.textContent = data.bpm;
        if (data.bpm < 60) {
            bpmStatus.textContent = "Bradicardia (Baixo)";
            bpmStatus.className = "bpm-status status-abnormal";
        } else if (data.bpm > 100) {
            bpmStatus.textContent = "Taquicardia (Alto)";
            bpmStatus.className = "bpm-status status-abnormal";
        } else {
            bpmStatus.textContent = "Batimento Normal";
            bpmStatus.className = "bpm-status status-normal";
        }

        if (data.accuracy !== undefined) {
            accuracyDisplay.textContent = data.accuracy + '%';
        }

        const layoutConfig = {
            plot_bgcolor: '#ffffff',
            paper_bgcolor: '#ffffff',
            font: { color: '#475569', family: 'Inter' },
            margin: { t: 40, b: 40, l: 40, r: 20 },
            xaxis: { gridcolor: '#e2e8f0', zerolinecolor: '#cbd5e1' },
            yaxis: { gridcolor: '#e2e8f0', zerolinecolor: '#cbd5e1' },
            legend: { orientation: "h", y: 1.1 }
        };

        // --- Plot Raw Signal ---
        const rawTrace = {
            x: data.time,
            y: data.raw,
            type: 'scatter',
            mode: 'lines',
            name: 'Sinal Bruto',
            line: { color: '#94a3b8', width: 1.5 }
        };

        Plotly.newPlot('chart-raw', [rawTrace], {
            ...layoutConfig,
            title: { text: 'Sinal Bruto (Com ruído da rede e linha de base)', font: {color: '#1e293b'} }
        }, {responsive: true, scrollZoom: true});


        // --- Plot Filtered Signal with Peaks ---
        const filteredTrace = {
            x: data.time,
            y: data.filtered,
            type: 'scatter',
            mode: 'lines',
            name: 'Sinal Filtrado',
            line: { color: '#0f766e', width: 2 }
        };

        // Picos Detectados pelo Algoritmo
        const detectedTime = data.detected_peaks_idx.map(i => data.time[i]);
        const detectedAmp = data.detected_peaks_idx.map(i => data.filtered[i]);
        const detectedTrace = {
            x: detectedTime,
            y: detectedAmp,
            type: 'scatter',
            mode: 'markers',
            name: 'Picos Detectados (R)',
            marker: { color: '#10b981', size: 8, symbol: 'cross' }
        };

        // Anotações Originais (Ground Truth)
        const trueTime = data.true_peaks_idx.map(i => data.time[i]);
        const trueAmp = data.true_peaks_idx.map(i => data.filtered[i]);
        const trueTrace = {
            x: trueTime,
            y: trueAmp,
            type: 'scatter',
            mode: 'markers',
            name: 'Anotações Originais',
            marker: { color: '#ef4444', size: 10, symbol: 'circle-open', line: {width: 2} }
        };

        Plotly.newPlot('chart-filtered', [filteredTrace, trueTrace, detectedTrace], {
            ...layoutConfig,
            title: { text: 'Sinal Filtrado & Detecção de Picos', font: {color: '#1e293b'} }
        }, {responsive: true, scrollZoom: true});
    }
});
