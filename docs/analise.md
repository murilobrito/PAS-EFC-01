# Documento de Análise de Violações SOLID (Sprint 0)

Este documento descreve as violações aos princípios SOLID encontradas no código original (`legacy.py`).

## 1. SRP (Single Responsibility Principle)

**Violação 1: Mistura de Regras de Negócio e Persistência**
- **Trecho Problemático:** `legacy.py`, linhas 6-13 (`__init__`) e métodos como `get_ped`, `upd_st`.
- **Justificativa Técnica:** A classe `Sis` está fortemente acoplada ao banco de dados SQLite. Ela gerencia conexões, executa queries cruas (SQL) e lida com a regra de negócios de pedidos ao mesmo tempo.
- **Impacto Prático:** Mudar o banco de dados (ex: para PostgreSQL) exigiria reescrever quase toda a classe. Testar a regra de negócios exige um banco de dados real.

**Violação 2: Mistura de Casos de Uso (Pedidos, Relatórios, Notificações)**
- **Trecho Problemático:** `legacy.py`, funções `gerar_rel` e prints em `add_ped` / `upd_st`.
- **Justificativa Técnica:** A mesma classe que cria pedidos também gera relatórios (`gerar_rel`) e emite notificações aos clientes (`print` imitando emails/SMS).
- **Impacto Prático:** Se o formato do relatório mudar ou se quisermos enviar notificações por outro canal (ex: WhatsApp), teremos que modificar a classe principal do sistema, aumentando o risco de quebrar o fluxo de pedidos.

---

## 2. OCP (Open-Closed Principle)

**Violação 1: Verificação Rígida de Tipos de Itens (Descontos)**
- **Trecho Problemático:** `legacy.py`, linhas 18-25 (`if i['tipo'] == 'normal' elif ...`).
- **Justificativa Técnica:** A classe está aberta para modificação. Cada vez que um novo tipo de desconto é criado, a função `add_ped` precisa ser alterada com um novo `elif`.
- **Impacto Prático:** A introdução do "desconto progressivo por volume" (requisito futuro) forçaria uma nova alteração nesse mesmo método central, aumentando as chances de regressão.

**Violação 2: Métodos de Pagamento Hardcoded**
- **Trecho Problemático:** `legacy.py`, linhas 119-135 (`if m == 'cartao' elif m == 'pix' ...`).
- **Justificativa Técnica:** A lógica de processamento de pagamento está centralizada com condicionais para cada método.
- **Impacto Prático:** Adicionar pagamento via criptomoeda (requisito futuro) exigirá modificar essa estrutura condicional, ferindo novamente o princípio OCP.

---

## 3. LSP (Liskov Substitution Principle)

**Violação 1: Supressão de Comportamento na Herança**
- **Trecho Problemático:** `legacy.py`, classe `PedEspecial`, método `upd_st` (linhas 183-190).
- **Justificativa Técnica:** A subclasse `PedEspecial` redefine a mudança de status ignorando todas as lógicas de notificação (emails, SMS) e de pontuação (pontos VIP/Corporativo) que a classe pai `Sis` provê. 
- **Impacto Prático:** Uma função que espera receber um objeto do tipo `Sis` e usar `upd_st` vai se deparar com ausência de notificações e recompensas, quebrando o contrato implícito da superclasse.

**Violação 2: Alteração Não Documentada das Regras de Negócio de Cálculo**
- **Trecho Problemático:** `legacy.py`, classe `PedEspecial`, método `add_ped` (linhas 164-181).
- **Justificativa Técnica:** A classe filha altera completamente a forma como as regras de negócio de descontos `vip` e `corporativo` são aplicadas (as ignora) e injeta um multiplicador hardcoded de `1.15`.
- **Impacto Prático:** Substituir `Sis` por `PedEspecial` no processamento gera totais radicalmente divergentes sem seguir as mesmas premissas de entrada.

---

## 4. ISP (Interface Segregation Principle)

**Violação 1: Interface "Faz-Tudo" Monolítica**
- **Trecho Problemático:** `legacy.py`, toda a classe `Sis`.
- **Justificativa Técnica:** Não existem interfaces delimitando contratos, forçando dependentes a consumirem a classe inteira. Um serviço que precisa apenas validar o estoque (`validar_estoque`) passa a depender de `gerar_rel`, `proc_pag`, e do acesso a banco de dados.
- **Impacto Prático:** Dificulta a componentização e os testes isolados, pois qualquer cliente da classe carrega o fardo das dependências do SQLite e das lógicas de pagamento/relatórios.

**Violação 2: Dependência Excessiva no Polimorfismo**
- **Trecho Problemático:** `legacy.py`, herança de `PedEspecial`.
- **Justificativa Técnica:** Como a interface `Sis` é inflada, a classe filha `PedEspecial` "herda" capacidades (como validar estoque ou gerar relatórios) que ela nem deveria expor ou que não se encaixam no seu propósito especial.
- **Impacto Prático:** Uma interface segregada separaria comportamentos de leitura (relatórios) e escrita (operações), evitando sobrecarga de métodos.

---

## 5. DIP (Dependency Inversion Principle)

**Violação 1: Dependência Direta de Infraestrutura (SQLite)**
- **Trecho Problemático:** `legacy.py`, linha 8 (`self.db = sqlite3.connect('loja.db')`).
- **Justificativa Técnica:** O módulo de alto nível (`Sis`) instancia diretamente um driver de baixo nível (`sqlite3`). Ele deveria depender de uma abstração (ex: uma interface de repositório).
- **Impacto Prático:** Para realizar testes unitários rápidos, não podemos trocar facilmente o SQLite por um mock ou em-memória de forma nativa sem usar monkeypatching em bibliotecas padrão, o que é um mau design.

**Violação 2: Instanciação Estática e Bibliotecas Acopladas**
- **Trecho Problemático:** `legacy.py`, linha 15 (`datetime.now()`) e `print` no meio do código.
- **Justificativa Técnica:** O código confia em saídas do sistema/console e no relógio interno instanciados diretamente em suas funções centrais. Em um bom sistema, serviços de log/notificação ou provedores de tempo seriam injetados.
- **Impacto Prático:** Impossibilita o teste determinístico de horários sem bibliotecas invasivas, além de dificultar o redirecionamento dos alertas (que atualmente estão `hardcoded` como `prints`).
