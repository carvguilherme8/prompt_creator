## Prompt Creator

Esse repositório foi criado com o objetivo de criar prompts de inicialização de agentes utilizando LLM's para aplicar em um projeto da disciplina Reinforcement Learning.

### Requisitos:
- Python 3.8+
- Dependências listadas em `requirements.txt`
- Ollama gemma:2b 
    - Caso opte por utilizar outro modelo, lembre-se de adaptar os códigos

### Objetivo:

Queremos criar conjuntos de prompts de inicialização em que cada um foca em uma propriedade como:

- clareza 
- especificidade 
- complexidade
- Entre outras

Quando uma propriedade for escolhida, os prompts criados a partir dela irão de péssimo nessa propriedade à ótimo nessa propriedade.

Os agentes terão conjuntos de prompts das mesmas propriedades. Desse modo, ao aplicá-los no nosso projeto e observarmos os resultados conseguiremos tirar conclusões a respeito da melhor maneira de se construir um prompt para essa finalidade.

### Utilização:

O repositório está organizado em uma divisão de 3 agentes: **Coder**, **Reviewer** e **Code Refiner**, ambos possuindo um arquivo com scripts e um notebook. Esses arquivos são bem semelhantes, diferindo principalmente na mensagem para a criação do primeiro prompt de cada propriedade.

O funcionamento dos notebooks é a seguinte:

1. Escolha a propriedade que deseja abordar e atribua-a como parâmetro na função `create_first_prompt`
    
    - Essa função criará um prompt que peca na propriedade escolhida

2. Crie uma mensagem que servirá de base para a criação dos próximos prompts dessa mesma propriedade e execute a função `create_following_prompts`

    - Essa mensagem pode ser algo como: "Crie um prompt mais {propriedade} que esse: 

3. Execute `create_following_prompts` quantas vezes desejar, armazene os resultados em uma lista e execute `add_prompt_to_json` para salvá-los em um .json

4. Repita o mesmo processo para outras propriedades

### Json

o Json retornado terá a seguinte estrutura (para 3 promps de uma propriedade):

``` json
[
  {
    "propriedade": "propriedade",
    "valor": 1, 
    "prompt": "prompt simples"
  },
  {
    "propriedade": "propriedade",
    "valor": 2,
    "prompt": "prompt com mais {propriedade} que o primeiro"
  },
  {
    "propriedade": "propriedade",
    "valor": 3,
    "prompt": "prompt com mais {propriedade} que o segundo"
    }
  ]
