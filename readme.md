# SuUAV: Uma ferramenta para construção de cenários de mobilidade com UAVs

# Resumo
O SuUAV é uma ferramenta desenvolvida para facilitar a integração de veículos aéreos não tripulados (UAVs) em cenários de simulação de tráfego urbano gerados pelo SUMO. A ferramenta permite a inserção de UAVs com diferentes padrões de mobilidade, a geração de vídeos da simulação e a exportação de arquivos de mobilidade para uso em simuladores de redes, como o ns-3. Este repositório contém o código-fonte da ferramenta, exemplos de uso e documentação detalhada.

---
# Estrutura do Repositório
```
/repositorio
│
├── /src                # Código-fonte da ferramenta SuUAV
├── /interface          # Código-fonte da interface para mapa interativo
├── /paserser           # Código-fonte do parser para leitura de configuração
├── all_configs.ini     # Exemplo de configuração com todos os parâmetros
├── example.ini         # Configuração para exemplo
├── example.ini         # Cenário de tráfego para uso de exemplo
├── minimo.ini          # Configuração para execução minima
├── README.md           # Este arquivo
├── LICENSE             # Licença do projeto (MIT)
└── requirements.txt    # Dependências do projeto
├── SuUAV.py            # Arquivo principal
```

Há também a documentação do projeto hospedada em https://mateussantos14.github.io/SuUAVDocs/example/

---

# Selos Considerados
Os selos considerados para este artefato são:
- **Disponíveis (SeloD)**: O código-fonte e os dados estão disponíveis neste repositório.
- **Funcionais (SeloF)**: A ferramenta pode ser executada e suas funcionalidades podem ser observadas.
- **Sustentáveis (SeloS)**: O código está modularizado, organizado e documentado.
- **Experimentos Reprodutíveis (SeloR)**: As principais reivindicações do artigo podem ser reproduzidas seguindo as instruções fornecidas.

---

# Informações Básicas

A execução da ferramenta se da através da execução de comandos no terminal e uso de interface gráfica para seleção da posição dos UAVs.

### Requisitos de Hardware
- Armazenamento: 50mb de espaço livre para a ferramenta


### Requisitos de Software

A ferramenta foi testada em Windows e Linux e funciona com as depêndencias que serão descritas instaladas

#### Sistema operacional recomendado

O processo de instalação é simplificado utilizando Sistemas de base Linux pois a instalação de depêndencias é unificada.


---

# Dependências
As principais dependências do projeto são:
- Python 3.11.4
- ffmpeg

As bibliotecas python utilizadas foram:
- geopandas 1.0.1 
- matplotlib 3.8.0
- Shapely
- descartes 1.1.0

# Instalação

### Instalação no Linux

Para instalar a ferramenta, execute:
```bash
sudo apt install python ffmpeg pip
git clone https://github.com/MateusSantos14/SuUAV.git
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Instalação no Windows

Instalar o python, o pip e o ffmpeg através dos executáveis presentes nos sites das respectivas organizações. Com os mesmos instalados, execute:
```bash
git clone https://github.com/MateusSantos14/SuUAV.git
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Teste mínimo

Rode o comando

```
python main.py --run -i minimo.ini
```

Após isso, será gerado o vídeo minimo_video.mp4 e o trace minimoUAV.xml

# Experimentos

A execução será dividida em duas etapas. 
- O teste do setup que abrira o mapa interativo para a seleção de pontos. Demora em torno de 5 segundos.
- Após o setup, a geração do vídeo e trace. A execução dura em torno de 2 minutos e 30 segundos.

Os valores de tempo podem variar de acordo com o dispositivo utilizado. Esses valores são referentes a execução em um processador Intel Core i5-10400f.

## Construção das configurações através de interface
Para testar a aplicação funcionando, o comando abaixo executará o mapa interativo para selecionar os pontos iniciais dos UAVs:
```
python main.py --setup -i example.xml
```
## Alterar parâmetros de mobilidade
Após isso, será gerado o arquivo de configuração example.ini, é possível alterar certos parâmetros da mobilidade dos UAVs. Se desejar, pode alterar para ver como se comporta.

## Exportação para trace e geração de vídeo
Em seguida, rode o comando e aguarde o vídeo ser gerado:
```
python main.py --run -i example.ini
```

Após isso, será gerado o vídeo example_video.mp4 e o trace exampleUAV.xml.

No vídeo será possível observar a simulação com a mobilidade dos UAVs integrada. Já o arquivo .xml está em formato hábil para ser exportado para simuladores de rede.

# LICENSE
Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.