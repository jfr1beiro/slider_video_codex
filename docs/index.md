# Documentação Técnica

Este diretório contém o prompt original (`mcp_robust_prompt.txt`) e a visão geral do projeto.

## Componentes Implementados

- **converter/video_ingest.py** – responsável por validar e extrair frames de vídeos.
- **converter/slide_generator.py** – pós-processamento, aplicação de texto e geração de slides otimizados.
- **app/services/exporter.py** – cria pacotes exportáveis (JSON + assets) prontos para build do APK.
- **app/viewmodel/session_state.py** – controla o estado do projeto.
- **app/view/screens/editor_screen.py** – camada de interação com operações básicas.

## Como evoluir

1. Complete as telas restantes do app (player e configurações).
2. Adapte o `SessionState` para persistência offline/online.
3. Alimente o pipeline de Buildozer para gerar o APK final.
