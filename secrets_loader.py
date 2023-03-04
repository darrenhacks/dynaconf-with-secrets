import os
import re
import config

from cryptography.fernet import Fernet, InvalidToken
from dynaconf.utils.boxing import DynaBox


DECRYPTION_KEY_VAR = "DECRYPT_KEY"
ENCRYPTED_KEY_REGEX = re.compile("^ENC[(].*[)]$")
ENCODING = "utf-8"


def new_key():
    """
    Used to bootstrap the application. Will return a new encryption/decryption key.

    :return: A new encryption/decryption key.
    """
    return Fernet.generate_key()


def enc(value):
    """
    Used to bootstrap the application. Will encrypt a value passed in using the application's
    encryption/decryption key. The value returned is in the format the application expects
    to find when processing settings, so it can be pasted directly wherever you are putting
    the encrypted properties.

    :param value: The value to encrypt.
    :return: The encrypted value.
    """
    key = _extract_decryption_key(config.settings)
    return enc_with_key(key, value)


def enc_with_key(key, value):
    """
    Used to bootstrap the application. Will encrypt a value passed in using the key passed in.

    :param key: The key to use top perform the encryption.
    :param value: The value to encrypt.
    :return: The encrypted value.
    """
    if key is None:
        return None

    f = Fernet(key)
    c = f.encrypt(bytes(value, ENCODING))
    return f"ENC({c.decode(ENCODING)})"


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Called by Dynaconf to do custom settings processing.

    :param obj:
    :param env:
    :param silent:
    :param key:
    :param filename:
    :return: void
    """
    try:
        decryption_key = _extract_decryption_key(obj)
        if decryption_key is None:
            return

        if key is None:
            _handle_box(obj, decryption_key)
        else:
            _handle_single_prop(obj, decryption_key, key)
    except (InvalidToken, ValueError):
        if not silent:
            raise


# Returns the encryption/decryption key defined for the application. Will return None if one is not present.
def _extract_decryption_key(obj):

    dynaconf_prefix = obj.ENVVAR_PREFIX_FOR_DYNACONF
    if type(dynaconf_prefix) is bool:
        decrypt_key_variable = DECRYPTION_KEY_VAR
    else:
        decrypt_key_variable = f"{dynaconf_prefix}_{DECRYPTION_KEY_VAR}"

    # Check for the environment variable first. Since the environment variable
    # loader for Dynaconf should be last in the list, we cannot count on
    # environment variables being present in the Dynaconf configuration yet. To
    # emulate Dynaconf's expected behaviour, we need to check environment variables
    # first and then look at the Dynaconf configuration.

    # First, with the Dynaconf prefix.
    key = os.getenv(decrypt_key_variable)
    if key is not None:
        return key

    # Next, without it.
    key = os.getenv(DECRYPTION_KEY_VAR)
    if key is not None:
        return key

    # Check the Dynaconf config with the Dynaconf prefix.
    if decrypt_key_variable in obj.keys():
        return obj.items.get(decrypt_key_variable)

    # Finally, check the Dynaconf config without the Dynaconf prefix.
    if DECRYPTION_KEY_VAR in obj.keys():
        return obj.items.get(DECRYPTION_KEY_VAR)

    # Not able to find it.
    return None


# Loops through a collection of settings.
def _handle_box(box, decryption_key):

    for key, value in box.items():
        if type(value) is DynaBox:
            _handle_box(value, decryption_key)
        elif type(value) is str:
            _handle_prop(box, decryption_key, key, value)


# Handles the case of Dynaconf asking the load method to process a single property.
def _handle_single_prop(obj, decryption_key, key):

    if key in obj.keys():
        _handle_prop(obj, decryption_key, key, obj[key])


# Handles a property.
def _handle_prop(obj, decryption_key, key, value):

    # It'll only handle strings of the format ENC({text}).
    if type(value) is str and ENCRYPTED_KEY_REGEX.match(value):
        enc_val = value[4:-1]
        dec_val = _dec(decryption_key, enc_val)
        if dec_val is not None:
            obj[key] = dec_val.decode(ENCODING)


# Decrypts a value.
def _dec(key, value):
    f = Fernet(key)
    return f.decrypt(value)
