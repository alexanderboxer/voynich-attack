"""Pseudo-VMS encoder package.

Generates pseudo-VMS cipher text from natural-language plaintext under
the algebra-cipher hypothesis. See `encoder.py` for the full design.

Basic use:

    from voynpy.pseudo_vms import PseudoVmsEncoder

    enc = PseudoVmsEncoder()
    cipher = enc.encode("Take ipecacuanha and water")
"""
from voynpy.pseudo_vms.encoder import PseudoVmsEncoder

__all__ = ['PseudoVmsEncoder']
