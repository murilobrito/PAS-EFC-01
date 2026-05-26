import pytest
from legacy import Sis

@pytest.fixture
def sis(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = Sis()
    yield s
    s.close()

def test_pagamento_cripto(sis):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Joao', itens, 'normal')
    
    # 2% fee -> 102
    assert sis.proc_pag(id_ped, 'cripto', 101.99) is False
    assert sis.proc_pag(id_ped, 'cripto', 102.0) is True
    assert sis.get_ped(id_ped)['st'] == 'aprovado'

def test_desconto_volume(sis):
    # 3 units -> 15% discount
    itens = [{'nome': 'p1', 'p': 100, 'q': 3, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Maria', itens, 'normal')
    pedido = sis.get_ped(id_ped)
    # 300 * 0.85 = 255.0
    assert pedido['tot'] == pytest.approx(255.0)

def test_whatsapp_notification(sis, capsys):
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Carlos', itens, 'normal')
    captured = capsys.readouterr()
    assert "WhatsApp enviado para Carlos: Pedido recebido!" in captured.out
    
    sis.proc_pag(id_ped, 'cartao', 100)
    captured = capsys.readouterr()
    assert "WhatsApp enviado para Carlos: Pedido aprovado!" in captured.out
