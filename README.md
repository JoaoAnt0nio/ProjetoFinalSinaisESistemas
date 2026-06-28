# 🫀 Dashboard Analítico de Sinais de ECG

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

Este projeto consiste em um **Sistema de Análise de Eletrocardiograma (ECG)** desenvolvido como Projeto Final da disciplina de **Sinais e Sistemas**. A aplicação consome, processa e renderiza sinais reais provenientes da renomada **MIT-BIH Arrhythmia Database**, comparando algoritmos computacionais com diagnósticos médicos reais (*ground truth*).

---

## 🎯 Objetivo do Projeto

O objetivo principal é demonstrar a aplicação prática do processamento digital de sinais em dados biomédicos reais. Para isso, o sistema:
1. Realiza a extração e leitura de formatos binários biomédicos (`.dat`, `.hea`, `.atr`).
2. Aplica **filtros digitais (Passa-Faixa / Butterworth)** para atenuar ruídos de alta frequência e oscilações da linha de base.
3. Utiliza uma implementação baseada no **Algoritmo de Pan-Tompkins** para detecção autônoma de complexos QRS (batimentos cardíacos).
4. Calcula a frequência cardíaca (BPM) média da amostra e sua **acurácia de detecção** cruzando os dados do algoritmo com as marcações feitas pelos especialistas médicos originais.

---

## 🧠 Arquitetura e Implementação Técnica

O projeto é estritamente modular, dividindo as responsabilidades de processamento matemático (Backend) e renderização visual e fluidez (Frontend).

### ⚙️ Backend (Python + Flask)
O núcleo de inteligência e processamento de sinais. 
- **Bibliotecas-chave**: `wfdb` (leitura de dados PhysioNet), `scipy.signal` (filtros e processamento matemático) e `numpy`.
- **Pipeline de Processamento (Pan-Tompkins)**:
  1. **Filtro Passa-Faixa**: Otimizado (5-15 Hz) para maximizar a energia do QRS, removendo interferências da rede elétrica e respiração.
  2. **Cálculo Derivativo**: Destaca as altas inclinações características do complexo QRS.
  3. **Função Não-Linear (Elevação ao Quadrado)**: Torna todas as amostras positivas e amplifica desvios não-lineares, atenuando ruídos residuais.
  4. **Integração por Janela Móvel (150ms)**: Produz informações da duração do sinal, gerando envelopes bem definidos sobre cada batimento.
  5. **Limiar Adaptativo (Threshold)**: Detecta os picos das ondas de forma inteligente com base na energia do sinal, reajustando ao pico R máximo (janela de 100ms).

### 🎨 Frontend (HTML / CSS / Vanilla JS)
Focado em Usabilidade (UX), renderização de alta performance e Design Moderno.
- **Design System**: Construído utilizando a técnica de *Glassmorphism*, paleta de cores *Dark/Light Mode* responsiva e tipografia moderna (Inter e Outfit).
- **Renderização Gráfica**: Injeção da biblioteca **Plotly.js** via CDN, capaz de renderizar milhares de amostras (pontos) em tempo real, sem travar o navegador, oferecendo Zoom e Pan interativos aos gráficos brutos e filtrados.

---

## 🚀 Como Executar o Projeto

O projeto não exige bancos de dados SQL/NoSQL complexos, operando inteiramente via arquivos estáticos binários.

### Pré-requisitos
Certifique-se de ter o Python instalado na sua máquina e instale as dependências:
```bash
pip install flask flask-cors wfdb scipy numpy
```

### Passo a Passo

**1. Inicie o Servidor de Processamento (Backend):**
Abra o terminal na pasta do projeto e navegue para o diretório `backend`:
```bash
cd backend
python app.py
```
*O servidor ficará escutando requisições na porta `5000` (http://localhost:5000).*

**2. Abra o Painel Visual (Frontend):**
Sem a necessidade de um servidor web como Apache ou NGINX, a interface foi desenvolvida para rodar diretamente via protocolo de arquivo.
- Basta dar dois cliques no arquivo `index.html` (dentro da pasta `frontend`).
- Ou abrir diretamente pelo navegador/terminal.

---

## 📊 Compreendendo a Interface

- **Seleção de Registro (Sidebar)**: Lista os arquivos de pacientes disponíveis.
- **Duração (Slider)**: Ajusta o recorte temporal analisado (em segundos). Recortes maiores aumentam a carga matemática.
- **Sinal Bruto (Raw Signal)**: Demonstra o sinal bruto exatamente como extraído do equipamento do MIT em 1980, onde é visível ruídos miográficos e flutuações de linha de base.
- **Sinal Processado**: Sinal após suavização. 
  - 🟩 As **Cruzes Verdes (+)** mostram os instantes (picos R) que o algoritmo matemático criado por nós identificou como batimento.
  - 🔴 Os **Círculos Vermelhos (o)** são as anotações exatas (Truth Labels) criadas pelos cardiologistas na época.
  - *A sobreposição de ambos os marcadores determina a **Acurácia** vista no painel lateral.*

---
Desenvolvido para fins acadêmicos e científicos.
