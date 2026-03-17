from voynpy.corpora import vms
from voynpy.reftext import RefText


def test_vms_loads():
    assert isinstance(vms, RefText)


def test_vms_token_count():
    assert len(vms.tklist) == 33669
