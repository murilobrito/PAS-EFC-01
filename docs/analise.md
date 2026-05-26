# Documento de Análise e Refatoração

## 8.1 (a) Identificação das Violações SOLID
No código original (`codigo_legado.py`), identificamos várias violações graves dos princípios SOLID:

*   **SRP (Single Responsibility Principle):** A classe `Sis` era um clássico "God Object". Ela gerenciava a conexão com o banco de dados SQLite, montava queries SQL, calculava os descontos de diferentes itens, validava pagamentos simulados e imprimia os relatórios e notificações.
    *   *Trecho problemático:* `def add_ped(self, n, its, t):` fazia inserts diretos no banco e enviava emails na mesma função.
*   **OCP (Open/Closed Principle):** Para adicionar uma nova regra de pagamento ou desconto, era obrigatório modificar a função base.
    *   *Trecho problemático:* Em `upd_st(self, id, s)` haviam múltiplos `if/elif` estáticos verificando `if t == 'vip'`, `elif t == 'corporativo'`, impedindo a extensão sem modificação do código central.
*   **LSP (Liskov Substitution Principle):** A classe `PedEspecial` herdava de `Sis`, mas sobrescrevia o comportamento de `upd_st` e `add_ped`, quebrando as pré-condições da superclasse (retornando e ignorando parâmetros).
    *   *Trecho problemático:* `class PedEspecial(Sis): def upd_st(self, id, s): ...`
*   **ISP (Interface Segregation Principle):** O acesso a dados não possuía uma interface definida; os serviços conheciam e dependiam diretamente do SQL cru, não havendo abstração.
*   **DIP (Dependency Inversion Principle):** Os serviços de alto nível dependiam diretamente dos detalhes de baixo nível (ex: a classe `Sis` manipulava o SQLite diretamente e estava acoplada aos `prints` e regras concretas).

## 8.2 (b) Soluções Implementadas
Para resolver essas violações de SRP, ISP e DIP (foco do Sprint 1), estruturamos as seguintes soluções:

*   **SRP Resolvido:** Criamos o pacote `services/` com o `OrderService` (gestão de pedidos) e o `ReportService` (geração de relatórios). Persistência de dados foi movida para `SQLiteOrderRepository`.
*   **ISP Resolvido:** Criamos a interface `OrderRepositoryInterface` definindo contratos específicos (`save`, `get`, `update_status`, etc.). As classes concretas são obrigadas a implementar apenas os métodos de persistência.
*   **DIP Resolvido:** O `OrderService` parou de instanciar o banco de dados. Agora ele recebe o `OrderRepositoryInterface` via construtor (Injeção de Dependências). Da mesma forma, as lógicas de desconto e pagamento foram passadas via injeção (`payment_strategies`, `item_strategies`).

## 8.3 (c) Diagrama UML de Classes

```mermaid
classDiagram
    class Sis {
        +order_service: OrderService
        +report_service: ReportService
        +add_ped(n, its, t)
        +get_ped(id)
        +upd_st(id, s)
    }

    class OrderService {
        -repository: OrderRepositoryInterface
        -observers: List[OrderObserver]
        -payment_strategies: Dict
        -discount_strategies: Dict
        +create_order(order)
        +process_payment(id, method, value)
        +update_status(id, status)
    }

    class OrderRepositoryInterface {
        <<interface>>
        +save(order)
        +get(id)
        +update_status(id, status)
    }

    class SQLiteOrderRepository {
        -db_path: str
        +save(order)
        +get(id)
        +update_status(id, status)
    }

    class PaymentStrategy {
        <<interface>>
        +process(value, total)
    }
    class PixStrategy
    class CartaoStrategy
    class CriptoStrategy

    class OrderObserver {
        <<interface>>
        +update(event_type, order_data)
    }
    class EmailNotifier
    class WhatsAppNotifier

    Sis --> OrderService
    OrderService --> OrderRepositoryInterface
    SQLiteOrderRepository ..|> OrderRepositoryInterface
    OrderService --> PaymentStrategy
    PaymentStrategy <|-- PixStrategy
    PaymentStrategy <|-- CartaoStrategy
    PaymentStrategy <|-- CriptoStrategy
    OrderService --> OrderObserver
    OrderObserver <|-- EmailNotifier
    OrderObserver <|-- WhatsAppNotifier
```

## 8.4 (d) Melhorias de Clean Code
*   **Nomenclatura:** Variáveis obscuras como `n`, `its`, `t`, `tot` e `st` foram substituídas por nomes descritivos (`cliente`, `itens`, `tipo_pedido`, `total`, `status`). 
*   **Complexidade Ciclomática:** A extração dos blocos gigantes `if/elif/else` para o padrão *Strategy* e *Observer* fragmentou as responsabilidades, diminuindo radicalmente a complexidade das funções centrais (que antes chegavam a ter 5 ou 6 ramificações profundas).
*   **Magic Strings/Numbers:** Substituídos por constantes ou comportamentos delegados nas subclasses (os descontos "20%", "10%" e o valor "1.5" do VIP viraram propriedades isoladas).

## 8.5 (e) Extensões Implementadas
Para provar que o OCP foi satisfeito, as três extensões obrigatórias foram adicionadas ao projeto **sem tocar no código existente do pacote `src/`**:

1.  **Pagamento em Criptomoeda:** Criada a classe `CriptoStrategy` (implementando `PaymentStrategy`) que avalia a cobrança de 2% (verificando se o `value` fornecido atinge `total * 1.02`). Ela foi injetada no dicionário da raiz (`legacy.py`).
2.  **Canal WhatsApp:** Criada a classe `WhatsAppNotifier` implementando a interface `OrderObserver`. Sem modificar o `OrderService`, o notifier foi injetado (via `attach()`) e começou a captar os eventos de `created` e `status_updated`.
3.  **Desconto Progressivo por Volume:** Em vez de mudar a interface de `ItemDiscountStrategy` ou modificar o `OrderService`, aplicamos o padrão *Decorator* com o `VolumeDiscountDecorator`. Ele "envelopa" qualquer estratégia já existente (como `NormalItemStrategy`) e aplica um desconto extra de 15% caso `quantidade >= 3`.

## 8.6 (f) Reflexão Metacognitiva
O maior desafio encontrado no processo de refatoração foi desvincular a lógica de notificação (que misturava regras de envio de e-mails, com cálculos de pontuação baseados no status e tipo VIP/Corporativo) de dentro do `OrderService`. A solução para esse alto acoplamento foi o padrão **Observer**, transformando o OrderService em um "publisher" agnóstico, o que permitiu que cada notificador avaliasse as informações recebidas independentemente. Isso trouxe um enorme alívio na legibilidade e facilitou imensamente a adição posterior do `WhatsAppNotifier`.


## 8.7 Sa�da dos Testes e M�tricas Autom�ticas

### Cobertura de Testes (pytest + coverage)
`	ext
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\projetos\Refatoracao-Limpa
configfile: pytest.ini
plugins: anyio-4.13.0, dash-4.1.0, cov-7.1.0
collected 22 items

tests\test_extensions.py ...                                             [ 13%]
tests\test_legacy_behavior.py ...................                        [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.1-final-0 _______________

Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
legacy.py                                         52      2    96%
src\__init__.py                                    0      0   100%
src\interfaces\__init__.py                         0      0   100%
src\interfaces\order_repository_interface.py      25      7    72%
src\models\__init__.py                             0      0   100%
src\models\item.py                                 8      1    88%
src\models\order.py                               14      0   100%
src\models\order_factory.py                       10      0   100%
src\observers\notification_observer.py            55      2    96%
src\observers\whatsapp_notifier.py                12      0   100%
src\repositories\__init__.py                       0      0   100%
src\repositories\sqlite_order_repository.py       43      0   100%
src\services\__init__.py                           0      0   100%
src\services\order_service.py                     64      4    94%
src\services\report_service.py                    26      0   100%
src\strategies\crypto_strategy.py                 11      0   100%
src\strategies\discount_strategy.py               33      2    94%
src\strategies\payment_strategy.py                30      5    83%
src\strategies\volume_discount_strategy.py         9      0   100%
------------------------------------------------------------------
TOTAL                                            392     23    94%
============================= 22 passed in 0.36s ==============================

`

### An�lise de Tipagem (Mypy)
`	ext
Success: no issues found in 18 source files

`
