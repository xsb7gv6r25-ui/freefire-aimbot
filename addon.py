#!/usr/bin/env python3
# ============================================
# FREEFIRE AIMBOT - 95% HEADSHOT
# ADDON PARA MITMPROXY (SOCKS5)
# VERSIÓN 4.0 - INDETECTABLE
# ============================================

import re
import json
from mitmproxy import http
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad

# ==========================================
# CONFIGURACIÓN AES (DE FREE FIRE)
# ==========================================

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

# ==========================================
# AIMBOT 95% (PARÁMETROS MODIFICADOS)
# ==========================================

AIMBOT_HEADSHOT = 95
AIMBOT_LOCK = 95
AIMBOT_FACTOR = 95

# ==========================================
# FUNCIONES DE CIFRADO/DESCIFRADO
# ==========================================

def decrypt_aes(data):
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted = cipher.decrypt(data)
        return unpad(decrypted, AES.block_size)
    except Exception:
        return data

def encrypt_aes(data):
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        padded = pad(data, AES.block_size)
        return cipher.encrypt(padded)
    except Exception:
        return data

# ==========================================
# MODIFICADOR DE PAQUETES (SOLO AIMBOT)
# ==========================================

def modify_packet(data):
    if not data:
        return data
    try:
        decrypted = decrypt_aes(data)
        data_str = decrypted.decode('utf-8', errors='ignore')
        if 'headlock' in data_str or 'aimlock' in data_str or 'aimbot_factor' in data_str:
            data_str = re.sub(r'"headlock":\d+', f'"headlock":{AIMBOT_HEADSHOT}', data_str)
            data_str = re.sub(r'"aimlock":\d+', f'"aimlock":{AIMBOT_LOCK}', data_str)
            data_str = re.sub(r'"aimbot_factor":\d+', f'"aimbot_factor":{AIMBOT_FACTOR}', data_str)
        encrypted = encrypt_aes(data_str.encode('utf-8'))
        return encrypted
    except Exception as e:
        print(f"Error: {e}")
        return data

class FreeFireAimbot:
    def __init__(self):
        self.packet_count = 0
        self.modified_count = 0
    def request(self, flow: http.HTTPFlow) -> None:
        if self._is_freefire(flow):
            self.packet_count += 1
            if flow.request.content:
                original = flow.request.content
                modified = modify_packet(original)
                if modified != original:
                    flow.request.content = modified
                    self.modified_count += 1
                    print(f"Petición modificada: {self.modified_count}")
    def response(self, flow: http.HTTPFlow) -> None:
        if self._is_freefire(flow):
            if flow.response and flow.response.content:
                original = flow.response.content
                modified = modify_packet(original)
                if modified != original:
                    flow.response.content = modified
                    self.modified_count += 1
                    print(f"Respuesta modificada: {self.modified_count}")
    def _is_freefire(self, flow) -> bool:
        domains = ['freefire', 'garena', 'ff']
        if hasattr(flow, 'request'):
            url = flow.request.pretty_url.lower()
            return any(domain in url for domain in domains)
        return False

addons = [FreeFireAimbot()]
