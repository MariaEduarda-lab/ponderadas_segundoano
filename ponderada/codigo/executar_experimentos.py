"""A4 — Executa nove processos isolados e salva as evidências reais da coleta.

Autora: Maria Eduarda Barbosa Oliveira. Usa somente a biblioteca padrão.
"""

import json
from datetime import datetime
from pathlib import Path
import platform
import subprocess
import sys
from zoneinfo import ZoneInfo


def main() -> None:
    """Sem parâmetros/retorno; executa 3 vezes cada versão e grava JSON/TXT.

    Cada subprocesso recebe 20.000 amostras. Timeout de 120 s é proteção
    externa, distinta do monitor interno de 1 s sem consumo; sua ocorrência
    gera erro explícito e não é convertida em resultado do experimento.
    """
    codigo = Path(__file__).resolve().parent
    imagens = codigo.parent / "img"
    imagens.mkdir(exist_ok=True)
    coleta = {
        "data": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
        "python": sys.version, "sistema": platform.platform(),
        "nome": "Maria Eduarda Barbosa Oliveira", "D1": 5, "D2": 7,
        "resultados": [],
    }
    for versao in (1, 2, 3):
        registro = [f"Coleta: {coleta['data']}", f"Python: {platform.python_version()}"]
        for repeticao in (1, 2, 3):
            comando = [sys.executable, str(codigo / f"versao{versao}.py")]
            processo = subprocess.run(comando, capture_output=True, text=True,
                                      timeout=120, check=True)
            saida = processo.stdout
            resultado = json.loads(saida)
            resultado["execucao"] = repeticao
            coleta["resultados"].append(resultado)
            bloco = (f"\n$ python3 ponderada/codigo/versao{versao}.py"
                     f"  # execução {repeticao}\n{saida.rstrip()}")
            registro.append(bloco)
            print(bloco, flush=True)
        (imagens / f"versao{versao}.txt").write_text("\n".join(registro) + "\n", encoding="utf-8")
    (codigo / "resultados.json").write_text(
        json.dumps(coleta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
