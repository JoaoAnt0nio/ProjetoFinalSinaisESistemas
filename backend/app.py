from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import wfdb
import numpy as np
import scipy.signal as signal

app = Flask(__name__)
CORS(app) # Habilita comunicação entre o frontend e o backend local

# Diretório onde a base de dados foi descompactada
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mit-bih-arrhythmia-database-1.0.0')

@app.route('/api/records', methods=['GET'])
def get_records():
    """Lista todos os registros disponíveis na base de dados."""
    records = []
    if os.path.exists(DB_DIR):
        for f in os.listdir(DB_DIR):
            if f.endswith('.hea'):
                records.append(f.replace('.hea', ''))
    return jsonify({"records": sorted(records)})

def pan_tompkins_detector(ecg_signal, fs):
    """
    Implementação simplificada do algoritmo de Pan-Tompkins para detecção de QRS.
    Retorna os índices onde os picos R foram encontrados.
    """
    # 1. Filtro Passa-Baixa e Passa-Alta (Bandpass ~ 5-15 Hz maximiza a energia do QRS)
    nyq = 0.5 * fs
    low = 5.0 / nyq
    high = 15.0 / nyq
    b, a = signal.butter(1, [low, high], btype='band')
    filtered = signal.filtfilt(b, a, ecg_signal)
    
    # 2. Derivada (destaca as inclinações altas do QRS)
    deriv = np.gradient(filtered)
    
    # 3. Elevação ao quadrado (torna tudo positivo e amplifica grandes inclinações)
    squared = deriv ** 2
    
    # 4. Integração por janela móvel (suavização)
    window_width = int(0.150 * fs) # 150 ms
    integrated = np.convolve(squared, np.ones(window_width)/window_width, mode='same')
    
    # 5. Detecção de picos usando um limiar adaptativo simples
    threshold = np.mean(integrated) * 1.5
    peaks, _ = signal.find_peaks(integrated, distance=int(0.2 * fs), height=threshold)
    
    # Ajustar a posição do pico detectado para o pico máximo no sinal original
    adjusted_peaks = []
    search_window = int(0.1 * fs) # 100 ms para cada lado
    for p in peaks:
        start = max(0, p - search_window)
        end = min(len(ecg_signal), p + search_window)
        # O pico R geralmente é o máximo absoluto naquela janela (pode ser invertido, mas vamos assumir positivo para MLII)
        local_max = start + np.argmax(ecg_signal[start:end])
        adjusted_peaks.append(int(local_max))
        
    return adjusted_peaks

@app.route('/api/process', methods=['GET'])
def process_record():
    record_name = request.args.get('record', '100')
    duration_sec = int(request.args.get('duration', 10)) # Analisar os primeiros X segundos
    
    record_path = os.path.join(DB_DIR, record_name)
    
    if not os.path.exists(record_path + '.dat'):
        return jsonify({"error": "Registro não encontrado"}), 404
        
    try:
        # Lê o registro (apenas o tempo selecionado para não sobrecarregar)
        # A base do MIT tem fs=360Hz. Entao duration * 360 frames.
        record = wfdb.rdrecord(record_path, sampto=duration_sec * 360)
        annotation = wfdb.rdann(record_path, 'atr', sampto=duration_sec * 360)
        
        # Pega o primeiro canal (geralmente MLII)
        ecg_raw = record.p_signal[:, 0]
        fs = record.fs
        
        # Filtro para limpeza de linha de base e alta frequência para exibição
        # Passa-faixa de 0.5Hz a 45Hz
        nyq = 0.5 * fs
        b_disp, a_disp = signal.butter(2, [0.5/nyq, 45/nyq], btype='band')
        ecg_filtered = signal.filtfilt(b_disp, a_disp, ecg_raw)
        
        # Detecção Algoritmica (Pan-Tompkins)
        detected_peaks = pan_tompkins_detector(ecg_raw, fs)
        
        # Anotações Originais (True Labels do Cardiologista)
        true_peaks = [int(s) for s in annotation.sample if annotation.symbol[annotation.sample.tolist().index(s)] in ['N', 'L', 'R', 'B', 'A', 'a', 'J', 'S', 'V', 'r', 'F', 'e', 'j', 'n', 'E', '/', 'f', 'Q', '?']]
        
        # Cálculo de BPM médio (usando picos detectados)
        if len(detected_peaks) > 1:
            rr_intervals = np.diff(detected_peaks) / fs # em segundos
            bpm = 60.0 / np.mean(rr_intervals)
        else:
            bpm = 0.0
            
        # Comparação Percentual (Acurácia)
        matched = 0
        tolerance = int(0.1 * fs) # Tolerância de 100ms para considerar o pico válido
        for tp in true_peaks:
            for dp in detected_peaks:
                if abs(tp - dp) <= tolerance:
                    matched += 1
                    break
        accuracy = (matched / len(true_peaks)) * 100 if len(true_peaks) > 0 else 0.0
            
        # Tempo (eixo X)
        time_axis = np.arange(len(ecg_raw)) / fs
        
        return jsonify({
            "time": time_axis.tolist(),
            "raw": ecg_raw.tolist(),
            "filtered": ecg_filtered.tolist(),
            "detected_peaks_idx": detected_peaks,
            "true_peaks_idx": true_peaks,
            "bpm": round(bpm, 1),
            "accuracy": round(accuracy, 1),
            "fs": fs
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
