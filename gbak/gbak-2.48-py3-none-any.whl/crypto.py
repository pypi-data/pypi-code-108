from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
from os import stat, remove, path

# pyAesCrypt version
version = "0.4.3"

# encryption/decryption buffer size - 64K
bufferSize = 64 * 1024

# maximum password length (number of chars)
maxPassLen = 1024

# AES block size in bytes
AESBlockSize = 16


# password stretching function
def stretch(passw, iv1):
    # hash the external iv and the password 8192 times
    digest = iv1 + (16 * b"\x00")

    for i in range(8192):
        passHash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        passHash.update(digest)
        passHash.update(bytes(passw, "utf_16_le"))
        digest = passHash.finalize()

    return digest


# encrypt file function
# arguments:
# infile: plaintext file path
# outfile: ciphertext file path
# passw: encryption password
# bufferSize: encryption buffer size, must be a multiple of
#             AES block size (16)
#             using a larger buffer speeds up things when dealing
#             with big files
def encryptFile(infile, outfile, passw, bufferSize, config):
    try:
        with open(infile, "rb") as fIn:
            # check that output file does not exist
            # or that, if exists, is not the same as the input file
            # (i.e.: overwrite if it seems safe)
            if path.isfile(outfile):
                if path.samefile(infile, outfile):
                    raise ValueError("Input and output files "
                                     "are the same.")
            try:
                with open(outfile, "wb") as fOut:
                    # encrypt file stream
                    encryptStream(fIn, fOut, passw, bufferSize, config)

            except IOError:
                raise IOError("Unable to write output file.")

    except IOError:
        raise IOError("File \"" + infile + "\" was not found.")


# encrypt binary stream function
# arguments:
# fIn: input binary stream
# fOut: output binary stream
# passw: encryption password
# bufferSize: encryption buffer size, must be a multiple of
#             AES block size (16)
#             using a larger buffer speeds up things when dealing
#             with long streams
def encryptStream(fIn, fOut, passw, bufferSize, config):
    # validate bufferSize
    if bufferSize % AESBlockSize != 0:
        raise ValueError("Buffer size must be a multiple of AES block size.")

    if len(passw) > maxPassLen:
        raise ValueError("Password is too long.")

    # generate external iv (used to encrypt the main iv and the
    # encryption key)
    iv1 = urandom(AESBlockSize)

    # stretch password and iv
    key = stretch(passw, iv1)

    # generate random main iv
    iv0 = urandom(AESBlockSize)

    # generate random internal key
    intKey = urandom(32)

    # instantiate AES cipher
    cipher0 = Cipher(algorithms.AES(intKey), modes.CBC(iv0),
                     backend=default_backend())
    encryptor0 = cipher0.encryptor()

    # instantiate HMAC-SHA256 for the ciphertext
    hmac0 = hmac.HMAC(intKey, hashes.SHA256(),
                      backend=default_backend())

    # instantiate another AES cipher
    cipher1 = Cipher(algorithms.AES(key), modes.CBC(iv1),
                     backend=default_backend())
    encryptor1 = cipher1.encryptor()

    # encrypt main iv and key
    c_iv_key = encryptor1.update(iv0 + intKey) + encryptor1.finalize()

    # calculate HMAC-SHA256 of the encrypted iv and key
    hmac1 = hmac.HMAC(key, hashes.SHA256(),
                      backend=default_backend())
    hmac1.update(c_iv_key)

    # write header
    fOut.write(bytes(config.get("DRIVE_SERVER"), "utf8"))

    # reserved byte (set to zero)
    fOut.write(b"\x00")


    # write "container" extension length
    fOut.write(b"\x00\x80")

    # write "container" extension
    for i in range(128):
        fOut.write(b"\x00")

    # write end-of-extensions tag
    fOut.write(b"\x00\x00")

    # write the iv used to encrypt the main iv and the
    # encryption key
    fOut.write(iv1)

    # write encrypted main iv and key
    fOut.write(c_iv_key)

    # write HMAC-SHA256 of the encrypted iv and key
    fOut.write(hmac1.finalize())

    # encrypt file while reading it
    while True:
        # try to read bufferSize bytes
        fdata = fIn.read(bufferSize)

        # get the real number of bytes read
        bytesRead = len(fdata)

        # check if EOF was reached
        if bytesRead < bufferSize:
            # file size mod 16, lsb positions
            fs16 = bytes([bytesRead % AESBlockSize])
            # pad data (this is NOT PKCS#7!)
            # ...unless no bytes or a multiple of a block size
            # of bytes was read
            if bytesRead % AESBlockSize == 0:
                padLen = 0
            else:
                padLen = 16 - bytesRead % AESBlockSize
            fdata += bytes([padLen]) * padLen
            # encrypt data
            cText = encryptor0.update(fdata) \
                    + encryptor0.finalize()
            # update HMAC
            hmac0.update(cText)
            # write encrypted file content
            fOut.write(cText)
            # break
            break
        # ...otherwise a full bufferSize was read
        else:
            # encrypt data
            cText = encryptor0.update(fdata)
            # update HMAC
            hmac0.update(cText)
            # write encrypted file content
            fOut.write(cText)

    # write plaintext file size mod 16 lsb positions
    fOut.write(fs16)

    # write HMAC-SHA256 of the encrypted file
    fOut.write(hmac0.finalize())


# decrypt file function
# arguments:
# infile: ciphertext file path
# outfile: plaintext file path
# passw: encryption password
# bufferSize: decryption buffer size, must be a multiple of AES block size (16)
#             using a larger buffer speeds up things when dealing with
#             big files
def decryptFile(infile, outfile, passw, bufferSize, config):
    try:
        with open(infile, "rb") as fIn:
            # check that output file does not exist
            # or that, if exists, is not the same as the input file
            # (i.e.: overwrite if it seems safe)
            if path.isfile(outfile):
                if path.samefile(infile, outfile):
                    raise ValueError("Input and output files "
                                     "are the same.")
            try:
                with open(outfile, "wb") as fOut:
                    # get input file size
                    inputFileSize = stat(infile).st_size
                    try:
                        # decrypt file stream
                        decryptStream(fIn, fOut, passw, bufferSize,
                                      inputFileSize, config)
                    except ValueError as exd:
                        # should not remove output file here because it is still in use
                        # re-raise exception
                        raise ValueError(str(exd))

            except IOError:
                raise IOError("Unable to write output file.")
            except ValueError as exd:
                # remove output file on error
                remove(outfile)
                # re-raise exception
                raise ValueError(str(exd))

    except IOError:
        raise IOError("File \"" + infile + "\" was not found.")


# decrypt stream function
# arguments:
# fIn: input binary stream
# fOut: output binary stream
# passw: encryption password
# bufferSize: decryption buffer size, must be a multiple of AES block size (16)
#             using a larger buffer speeds up things when dealing with
#             long streams
# inputLength: input stream length
def decryptStream(fIn, fOut, passw, bufferSize, inputLength, config):
    # validate bufferSize
    if bufferSize % AESBlockSize != 0:
        raise ValueError("Buffer size must be a multiple of AES block size")

    if len(passw) > maxPassLen:
        raise ValueError("Password is too long.")

    fdata = fIn.read(len(config.get("DRIVE_SERVER")))
    # check if file is in AES Crypt format (also min length check)
    if (fdata != bytes(config.get("DRIVE_SERVER"), "utf8") or inputLength < 136):
        raise ValueError("Error SV")

    # skip reserved byte
    fIn.read(1)

    # skip all the extensions
    while True:
        fdata = fIn.read(2)
        if len(fdata) != 2:
            raise ValueError("File is corrupted.")
        if fdata == b"\x00\x00":
            break
        fIn.read(int.from_bytes(fdata, byteorder="big"))

    # read external iv
    iv1 = fIn.read(16)
    if len(iv1) != 16:
        raise ValueError("File is corrupted.")

    # stretch password and iv
    key = stretch(passw, iv1)

    # read encrypted main iv and key
    c_iv_key = fIn.read(48)
    if len(c_iv_key) != 48:
        raise ValueError("File is corrupted.")

    # read HMAC-SHA256 of the encrypted iv and key
    hmac1 = fIn.read(32)
    if len(hmac1) != 32:
        raise ValueError("File is corrupted.")

    # compute actual HMAC-SHA256 of the encrypted iv and key
    hmac1Act = hmac.HMAC(key, hashes.SHA256(),
                         backend=default_backend())
    hmac1Act.update(c_iv_key)

    # HMAC check
    if hmac1 != hmac1Act.finalize():
        raise ValueError("Wrong password (or file is corrupted).")

    # instantiate AES cipher
    cipher1 = Cipher(algorithms.AES(key), modes.CBC(iv1),
                     backend=default_backend())
    decryptor1 = cipher1.decryptor()

    # decrypt main iv and key
    iv_key = decryptor1.update(c_iv_key) + decryptor1.finalize()

    # get internal iv and key
    iv0 = iv_key[:16]
    intKey = iv_key[16:]

    # instantiate another AES cipher
    cipher0 = Cipher(algorithms.AES(intKey), modes.CBC(iv0),
                     backend=default_backend())
    decryptor0 = cipher0.decryptor()

    # instantiate actual HMAC-SHA256 of the ciphertext
    hmac0Act = hmac.HMAC(intKey, hashes.SHA256(),
                         backend=default_backend())

    while fIn.tell() < inputLength - 32 - 1 - bufferSize:
        # read data
        cText = fIn.read(bufferSize)
        # update HMAC
        hmac0Act.update(cText)
        # decrypt data and write it to output file
        fOut.write(decryptor0.update(cText))

    # decrypt remaining ciphertext, until last block is reached
    while fIn.tell() < inputLength - 32 - 1 - AESBlockSize:
        # read data
        cText = fIn.read(AESBlockSize)
        # update HMAC
        hmac0Act.update(cText)
        # decrypt data and write it to output file
        fOut.write(decryptor0.update(cText))

    # last block reached, remove padding if needed
    # read last block

    # this is for empty files
    if fIn.tell() != inputLength - 32 - 1:
        cText = fIn.read(AESBlockSize)
        if len(cText) < AESBlockSize:
            raise ValueError("File is corrupted.")
    else:
        cText = bytes()

    # update HMAC
    hmac0Act.update(cText)

    # read plaintext file size mod 16 lsb positions
    fs16 = fIn.read(1)
    if len(fs16) != 1:
        raise ValueError("File is corrupted.")

    # decrypt last block
    pText = decryptor0.update(cText) + decryptor0.finalize()

    # remove padding
    toremove = ((16 - fs16[0]) % 16)
    if toremove != 0:
        pText = pText[:-toremove]

    # write decrypted data to output file
    fOut.write(pText)

    # read HMAC-SHA256 of the encrypted file
    hmac0 = fIn.read(32)
    if len(hmac0) != 32:
        raise ValueError("File is corrupted.")

    # HMAC check
    if hmac0 != hmac0Act.finalize():
        raise ValueError("Bad HMAC (file is corrupted).")
