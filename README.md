# Ponderada Computação CC08: do pipeline ao deadlock

**Autora:** Maria Eduarda Barbosa Oliveira.

Análise da pulseira sensorial Tato: arquitetura, pipeline, concorrência, deadlock e decisão de produção.

O relatório está em [ponderada/ponderada-tato.md](ponderada/ponderada-tato.md). Parâmetros: **D1 = 5, D2 = 7, N = 5**.

Requisito: Python 3.10 ou superior. Os experimentos usam somente a biblioteca padrão. Na raiz do repositório, cada comando executa uma versão com 20.000 amostras:

```bash
python3 ponderada/codigo/versao1.py
python3 ponderada/codigo/versao2.py
python3 ponderada/codigo/versao3.py
```

A versão 1 contém uma corrida proposital. A versão 3 contém um deadlock proposital. Um monitor encerra a execução depois de 1 segundo sem consumo; não é necessário interromper manualmente. Cada processo executa somente um experimento e suas threads são encerradas com ele.

Para executar novamente a bateria completa (três execuções de cada versão):

```bash
python3 ponderada/codigo/executar_experimentos.py
```

Esse comando atualiza `ponderada/codigo/resultados.json` e os registros `.txt` em `ponderada/img`. Os resultados da versão 1 dependem do escalonamento. A tabela do relatório registra a coleta entregue, e não é atualizada automaticamente ao repetir a bateria.

As capturas das execuções e das caches estão em `ponderada/img`, acompanhadas dos registros de terminal. Ao repetir os testes para uma nova entrega, atualize também a tabela e as capturas correspondentes.

O commit da entrega é identificado pela tag anotada `PONDERADA-CC08`, criada em 06/11/2026.
