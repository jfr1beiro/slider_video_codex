# MCP Robust APK Builder

Ferramentas em Python para dar sequência ao MCP descrito em `docs/mcp_robust_prompt.txt`. O objetivo é
prover rotinas reutilizáveis para ingestão de vídeos, geração/edição de slides e empacotamento dos
artefatos que serão usados pelo app Android.

## Estrutura

```
app/
  main.py            # CLI (argparse) para orquestrar ingestão → geração → exportação
  services/exporter.py
  viewmodel/session_state.py
  view/screens/editor_screen.py
converter/
  video_ingest.py    # extração de frames (OpenCV)
  slide_generator.py # pós-processamento com Pillow
```

## Fluxo recomendado

1. **Ingestão** – `python -m app.main ingest caminho/do/video.mp4 --fps 2`
2. **Geração de slides** – `python -m app.main generate-slides --output ./build/slides`
3. **Exportação** – `python -m app.main export --destination ./build/export`
4. **UI Kivy** – `python -m app.main ui` abre uma janela com drag-and-drop para repetir a ingestão
   diretamente na interface.

A CLI mantém um `SessionState` em memória para facilitar testes rápidos; em produção, a camada de ViewModel
deve persistir esse estado em banco ou storage conforme o MCP.

## Dependências

Instale os requisitos básicos:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para desenvolvimento, inclua também os extras:

```bash
pip install -e .[dev]
```

### UI em Kivy

Para visualizar e testar o pipeline com uma interface gráfica, rode o comando:

```bash
python -m app.main ui
```

O app abrirá uma janela com fundo escuro e uma área central. Arraste um vídeo (MP4/AVI) para
essa área para disparar automaticamente a ingestão usando o mesmo pipeline da CLI. Os frames
gerados são colocados no `SessionState`, permitindo continuar o fluxo usando os demais
subcomandos sem reiniciar o processo.

## Testes

Execute a suíte Pytest:

```bash
pytest
```

## Próximos Passos

- Implementar UI completa no Kivy com drag-and-drop.
- Integrar pipeline de exportação com build real de APK (Buildozer/Github Actions).
- Conectar armazenamento em nuvem para vídeos e slides.
