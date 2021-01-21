from Crypto.Cipher import AES

key = b'\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
iv = b'\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    
def encrypt_md(message,mode):
    print("Encrypting using", mode)
    print("message :",bytes(message))
    obj = AES.new(key, AES.MODE_CFB,iv)
    ciphertext=obj.encrypt(bytes(message))
    print("ciphertext: ",list(ciphertext))
    return list(ciphertext) 

def decrypt_md(ciphertext,mode):
    print("Decrypting using", mode)
    print("ciphertext received : ",list(ciphertext))
    obj2 = AES.new(key, AES.MODE_CFB,iv)
    message=obj2.decrypt(bytes(ciphertext))
    print("message received:",list(message))
    ciphertext = None
    return message 
  