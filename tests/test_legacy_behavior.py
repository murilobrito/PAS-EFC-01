import pytest
import os
import json
from legacy import Sis

@pytest.fixture
def sis(tmp_path, monkeypatch):
    """Isola o banco em diretorio temporario por teste."""
    monkeypatch.chdir(tmp_path)
    s = Sis()
    yield s
    s.close()

def test_pedido_normal_calcula_total_corretamente(sis):
    itens = [
        {'nome': 'produto1', 'p': 100, 'q': 2, 'tipo': 'normal'},
        {'nome': 'produto2', 'p': 50, 'q': 1, 'tipo': 'desc10'},
        {'nome': 'produto3', 'p': 100, 'q': 1, 'tipo': 'desc20'},
        {'nome': 'produto4', 'p': 200, 'q': 1, 'tipo': 'frete_gratis'},
    ]
    id_ped = sis.add_ped('Joao Silva', itens, 'normal')
    pedido = sis.get_ped(id_ped)
    # Total esperado: 100*2 + 50*1*0.9 + 100*1*0.8 + 200 = 200 + 45 + 80 + 200 = 525.0
    assert pedido['tot'] == pytest.approx(525.0)
    assert pedido['st'] == 'pendente'

def test_pedido_vip_aplica_desconto_de_5_por_cento(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Maria', itens, 'vip')
    pedido = sis.get_ped(id_ped)
    assert pedido['tot'] == pytest.approx(95.0)

def test_pedido_corporativo_aplica_desconto_de_10_por_cento(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Corp', itens, 'corporativo')
    pedido = sis.get_ped(id_ped)
    assert pedido['tot'] == pytest.approx(90.0)

def test_pagamento_insuficiente_falha(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    assert sis.proc_pag(id_ped, 'cartao', 50) is False

def test_pix_aprova_pedido_automaticamente(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    assert sis.proc_pag(id_ped, 'pix', 100) is True
    assert sis.get_ped(id_ped)['st'] == 'aprovado'

def test_cartao_aprova_pedido(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    assert sis.proc_pag(id_ped, 'cartao', 100) is True
    assert sis.get_ped(id_ped)['st'] == 'aprovado'

def test_boleto_aprova_pedido(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    assert sis.proc_pag(id_ped, 'boleto', 100) is True
    assert sis.get_ped(id_ped)['st'] == 'pendente'

def test_pagamento_invalido(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    assert sis.proc_pag(id_ped, 'cripto', 100) is False

def test_proc_pag_pedido_inexistente(sis):
    assert sis.proc_pag(999, 'cartao', 100) is False

def test_upd_st_normal_entregue(sis, capsys):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    sis.upd_st(id_ped, 'entregue')
    captured = capsys.readouterr()
    assert 'Cliente ganhou 100 pontos' in captured.out

def test_upd_st_vip_entregue(sis, capsys):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Maria', itens, 'vip')
    sis.upd_st(id_ped, 'entregue')
    captured = capsys.readouterr()
    assert 'ganhou 190 pontos' in captured.out

def test_upd_st_corporativo_entregue(sis, capsys):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Corp', itens, 'corporativo')
    sis.upd_st(id_ped, 'entregue')
    captured = capsys.readouterr()
    assert 'ganhou 135 pontos' in captured.out

def test_upd_st_enviado(sis, capsys):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    sis.upd_st(id_ped, 'enviado')
    captured = capsys.readouterr()
    assert 'Pedido enviado' in captured.out

def test_validar_estoque(sis):
    itens_validos = [{'nome': 'produto1', 'p': 10, 'q': 10}]
    assert sis.validar_estoque(itens_validos) is True

    itens_invalidos = [{'nome': 'produto1', 'p': 10, 'q': 200}]
    assert sis.validar_estoque(itens_invalidos) is False

    itens_inexistentes = [{'nome': 'nao_existe', 'p': 10, 'q': 1}]
    assert sis.validar_estoque(itens_inexistentes) is False

def test_cancelar_pedido(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    sis.cancelar_pedido(id_ped)
    assert sis.get_ped(id_ped)['st'] == 'cancelado'

def test_gerar_relatorios(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    sis.add_ped('Joao', itens, 'normal')
    
    sis.gerar_rel('vendas')
    assert os.path.exists('rel_vendas.txt')
    
    sis.gerar_rel('clientes')
    assert os.path.exists('rel_clientes.txt')

def test_ped_especial_add_ped(sis):
    itens = [
        {'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'},
        {'nome': 'p2', 'p': 100, 'q': 1, 'tipo': 'desc10'},
        {'nome': 'p3', 'p': 100, 'q': 1, 'tipo': 'desc20'},
    ]
    id_ped = sis.add_ped('Joao', itens, 'especial')
    pedido = sis.get_ped(id_ped)
    # 100 + 90 + 80 = 270. 270 * 1.15 = 310.5
    assert pedido['tot'] == pytest.approx(310.5)

def test_ped_especial_upd_st(sis, capsys):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'especial')
    sis.upd_st(id_ped, 'qualquer_coisa')
    captured = capsys.readouterr()
    assert 'Pedido especial' in captured.out

def test_main():
    from legacy import main
    main()
