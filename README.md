# Dynaconf and Local Secrets

This application exists so I can try out [Dynaconf](https://www.dynaconf.com). Of possible interest to others is the 
code to load encrypted properties. The general use case is for a team that needs to share secrets for a local 
development environment. This allows the team to share only a single key where the remaining properties can be 
encrypted and stored in a file added to a repository. While it is not suitable for production secrets, it's good enough 
for ones running on a developer's machine.

## Running

You will need to define a few environment variables to run the application.

- ENV_FOR_DYNACONF tells the application what environment you're running in. This should be `deveopment` or `production` for this sample.
- DYNACONF_DECRYPT_KEY is the encryption and decryption key. See below on how to generate this for your application.
- LOADERS_FOR_DYNACONF should have the value `['secrets_loader', 'dynaconf.loaders.env_loader']`

*NOTE*: since you do not have my encryption and decryption key, running the application out of the box will not allow
you to decrypt the encrypted properties. See below on how to bootstrap the application.

## Bootstrapping

Delete the encrypted properties in [settings.yaml](./settings.yaml). These are just a placeholder to demonstrate
what they look like in the files and will likely cause issues with the steps below.

The first thing you need is and encryption and decryption key. Call the `new_key()` method in 
[secrets_loader.py](./secrets_loader.py) to generate the new key. Assign this value to the `DYNACONF_DECRYPT_KEY`
environment variable. Remove the "b" that precedes the key string when passing in the environment variable. You will
probably need to keep the single quote around the key when passing it as an environment variable.

Next, you will need some encrypted values. Call the `enc_with_key()` method in [secrets_loader.py](./secrets_loader.py) passing
in the message you want to encrypt and the key from the previous step. The function returns the cypher text in the format 
needed by the application, so you can copy and paste the value directly into the [settings.yaml](./settings.yaml) file.