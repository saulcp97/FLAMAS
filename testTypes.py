import codecs


content = codecs.encode("GET WEIGHTS").decode()

print(content)

pickle.loads(codecs.decode(codes[0].encode(), "base64"))