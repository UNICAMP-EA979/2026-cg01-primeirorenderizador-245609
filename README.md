[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Ds6bJMe6)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23827939&assignment_repo_type=AssignmentRepo)
# Meu Primeiro Renderizador
#RAs: 243360 Rafael Andre Alves de Siqueira

Esta atividade é focada na implementação do estágio de geometria de um renderizador. O estágio de geometria é responsável por realizar operações por triângulo e vértices, em ordem:

- Shading de Vértices: mapeia os vértices entre espaços (model->world->camera->view volume) utilizando transformaçõe incluindo rotações, translações, escala e projeções
- Clipping: checa por vértices fora do volume de visão, removendo triângulos complementamente fora de visão e reconstruindo triângulos parcialmente visíveis
- Mapeamento na tela: mapeia os triângulos para o espaço da tela

Como simplificação nesta atividade, iremos implementar um renderizador utilizando Matplotlib, realizando os estágios e desenhando os triângulos na CPU. Também simplificaremos o estágio de clipping, removendo completamente também os triângulos parcialmente visíveis, o que não aconteceria em uma pipeline real. Por fim, o método de renderização utilizado não permite o uso de algorítmos de oclusão sofisticados e vamos utilizar o algoritmo do pintor, com suas limitações que serão exploradas na atividade.

Além do estágio de geometria, trabalharemos no estágio de aplicação. Assim como diversas aplicações gráficas, vamos implementar um "scene graph", onde cada objeto a ser renderizado é um nó em uma árvore, tendo sua posição no mundo influenciada pelos nós anteriores a ele.

## Estrutura da atividade

Esta atividade faz parte de uma sequência de atividades de computação gráfica. Elas possuem dependências entre si, onde o código de uma atividade anterior poderá ser reutilizado futuramente. Como esta é a primeira atividade, não existem dependências.

Os códigos a serem implementados podem estar em duas pastas diferentes: "src" para implementações do pacote do renderizador em si, "entrypoints" para códigos que usarão o renderizador implementado para desenhar cenas. Os entrypoints podem ser úteis para checar as implementações do pacote.

> Procure por trechos com `## SEU CÓDIGO AQUI` 

A entrega deve ser pelo GitHub, consistindo tanto do código desenvolvido quanto de imagens e vídeos gerados.

## Tarefas a serem realizadas

Os arquivos indicados possuem mais informações quando necessário.

### urenderer

- [ ] urenderer/node/node.py: implemente a construção de matrizes de transformação para rotação, translação e escala, junto da concatenação dessas transformações.
- [ ] urenderer/node/camera.py: implemente a construção da matriz de projeção perspectiva.

> $$  P = \begin{bmatrix}
> c/a & 0 & 0                                                    & 0 \\
> 0   & c & 0 & 0 \\
> 0   & 0 & -{{f^{\prime}+n^{\prime}}\over{f^{\prime}-n^{\prime}}} & -{{2f^{\prime}n^{\prime}}\over{f^{\prime}-n^{\prime}}} \\
> 0 & 0 & -1 & 0 \\
> \end{bmatrix} $$
> 
>   - $f^{\prime}$ é o far plane (em coordenadas positivas)
>   - $n^{\prime}$ é o near plane (em coordenadas positivas)
>   - $a$ é o aspecto da tela: $width/height$
>   - $c = 1.0/\tan{(\phi/2)}$, em que $\phi$ é o FoV vertical da câmera.

- [ ] urenderer/aplication/runtime.py: implemente a construção da matriz de transformação de modelo final de cada nó
- [ ] urenderer/renderer/pyplot_renderer.py: implemente os estágios de geometria

### Entrypoints

- [ ] 01-first_cube.py: este arquivo já está finalizado. Utilize-o para testar o código do renderizador.
- [ ] 02-pyramid.py: crie uma cena com uma pirâmide
- [ ] 03-grandchild.py: crie uma cena com vários objetos filhos um do outro.
- [ ] 04-intersection.py: explore a limitação do algoritmo de oclusão utilizado.
- [ ] 05-animation.py (OPCIONAL): crie uma animação simples.

## Executando o código

1. Instale o pacote na pasta raiz do repositório: `python -m pip install -e .`
   - Observe que o comando instala o pacote no modo editável (opção `-e`), isto significa que qualquer modificação que você fizer nele é diretamente refletida ao utilizar.
2. Execute os entrypoings na pasta "entrypoints": `python xx-nome.py`

Obs: utilize `python` ou `python3` de acordo com seu sistema.

## Correção

As tarefas do urenderer valem 60% da nota, enquanto que os entrypoints valem 40%.

Testes são executados para avaliar as tarefas do urenderer. Você pode testar seu código utilizando o `pytest` e também verificar sua pontuação no GitHub.

**NÃO ALTERE O CÓDIGO DOS TESTES**
