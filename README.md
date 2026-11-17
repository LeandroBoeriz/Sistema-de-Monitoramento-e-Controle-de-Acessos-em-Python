# PROJETO P2 — SISTEMA DE MONITORAMENTO E CONTROLE DE ACESSOS

## Como executar
Extraia o ZIP, abra a pasta no VS Code e, no terminal, execute:
    py .\Projeto_P2_LPII\Projeto_P2\sistema.py
Se seu computador usa o comando python ou python3, substitua py.
O projeto usa apenas a biblioteca padrão do Python 3.

## Cliente e servidor
Escolha a opção 7. O sistema inicia o servidor no próprio computador
(127.0.0.1), conecta o cliente, envia uma mensagem e mostra a resposta.
As duas pontas usam sockets TCP. Basta um terminal.

## Roteiro para a apresentação
1. Escolha 6 antes do primeiro login para demonstrar o tratamento de
   arquivo ausente, em uma pasta sem acessos.txt.
2. Use 1 para criar Admin como administrador e Ana como usuária comum.
   Use senhas fictícias e lembre-se delas. O primeiro administrador
   pode ser criado sem autorização prévia. Outros exigem um administrador.
3. Cadastre Ana novamente e mostre a prevenção de nomes duplicados.
   Use 2 e 3 para mostrar perfil e status.
4. Use 4 e faça um login correto com Ana. Depois erre a senha três
   vezes seguidas. Tente fazer o login correto e observe o bloqueio.
5. Use 5. Primeiro demonstre que Ana, enquanto conta comum ativa,
   não pode gerenciar usuários (faça esse teste antes dos três erros).
   Depois entre com Admin, informe Ana e escolha 2 para reativar.
   Faça um novo login correto com Ana.
6. Use 6 e entre com Admin para consultar os registros.
7. Use 8 para mostrar a alteração nas duas referências e o resultado
   de is. Use 7 para mostrar a mensagem e a resposta.
8. Digite uma opção inexistente. Depois use 0 para sair.

## Para explicar o código
- usuarios é um dicionário. A chave é o nome normalizado e o valor é o
  objeto Usuario ou Administrador.
- Administrador herda o login e redefine permissao().
- Login correto e reativação zeram o contador de senhas incorretas.
- Os usuários duram enquanto o programa estiver aberto. Apenas os eventos
  ficam em acessos.txt, criado automaticamente, sem senhas.
- A senha do exercício fica em memória e aparece durante a digitação.
  Use somente dados fictícios. Este é um exemplo acadêmico local.
