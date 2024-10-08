# eBoi Web 🐂

## Requisições

### O que deverá ser entregue: 

- Uma aplicação Web com as seguintes funções:
- Tela de login com validação de usuário;
- Tela de cadastro de usuários (somente para usuário Admin);
- Tela de edição e remoção de usuários (somente para usuário Admin);
- Tela para cadastro de sensores e atuadores (somente para usuário Admin);
- Tela para edição e remoção de usuários (somente para usuário Admin);
- Tela para visualização dos dados em Tempo Real (todos usuários tem acesso) coletados via MQTT Flask oriundos de uma aplicação do RA1, sendo por sistema físico (ESP32 por exemplo) ou via Wokwi;
- Tela para comandos remotos (todos usuários tem acesso) utilizando Flask mqtt para publicar na aplicação em ESP32 ou Wokwi;
 
### Requisitos mínimos da Fase 2 do PjBL: 

- Utilização de Flask;
- Uso do framework, layouts e componentes estudados no TDE2;
- CRUD para Usuários, sensores e atuadores;
- Comunicação com Broker MQTT para realizar funções subscribe e publish;
- Realizar comandos remotos pela aplicação desenvolvida em Flask;
- Ausência de bugs;
- Respeitar as seguintes regras:
- Somente um usuário Admin;
- Somente Admin pode criar, editar e deletar usuários, sensores e atuadores;
- Somente Admin pode listar usuários; 
- Todos usuários podem listar sensores e atuadores e acessar dashboards de recebimento de dados via MQTT Flask;
- Todos usuários podem acessar tela de comandos remotos via MQTT Flask para enviar dados ao BROKER;
