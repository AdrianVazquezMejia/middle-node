from Crypto.Cipher import AES
import logging

"""! 
    @var Key               secret key to use in the cipher  
    @var iv                vector to use for encryption or decryption
"""

key = b'\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
iv = b'\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'


log = logging.getLogger('cipher')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def encrypt_md(message, mode):
    """! Encrypts nodes' information

    @param message               message received  
    @param mode                  chaining mode to use for encryption

    @return list(ciphertext)     list with encrypted nodes' information
    """
    log.debug("Encrypting using %s", mode)
    log.debug("message : %s", str(bytes(message)))
    obj = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = obj.encrypt(bytes(message))
    log.debug("ciphertext: %s", str(list(ciphertext)))
    return list(ciphertext)


def decrypt_md(ciphertext, mode):
    """! Decrypt the information from the node

    @param ciphertext      data received from the node
    @param mode            chaining mode to use for decryption

    @return message        decrypted message
    """
    log.debug("Decrypting using %s", mode)
    log.debug("ciphertext received : %s", str(list(ciphertext)))
    obj2 = AES.new(key, AES.MODE_CFB, iv)
    message = obj2.decrypt(bytes(ciphertext))
    log.debug("message received: %s", str(list(message)))
    ciphertext = None
    return message
