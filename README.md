# python-pmc-restapi-client

pmc-restapi-client is a python package that provides a simple way to communicate to
RESTful APIs. It acts as a convenience wrapper around the requests package and abstracts
away the handling of URLs, (de)serialization, and request processing. Currently JSON
(de)serialization is supported.

## Install

### Regular use _(assuming that you've already published your package on NCBI Artifactory PyPI)_:

```sh
pip install pmc-restapi-client  # or add it to your requirements file
```

### For development:

Before you run scripts from misc/ folder make sure you 
installed pipenv independently of your virtual environments, 
for example you may want to consider using `pipx` 
to install various python package/scripts in kind 
of `standalone` mode.

```sh
ssh://git@bitbucket.be-md.ncbi.nlm.nih.gov:9418/pmc/python-pmc-restapi-client.git
cd python-pmc-restapi-client
misc/run_pipenv_init.sh 
misc/run_pip_install_req_dev.sh 
```

Then do your development. 

### Notes:

- Do not forget to create new git tags
(to keep version of the package bumped/updated). 
- Do not forget to update CHANGELOG.md. 
- Do not forget to add descriptions to doc/*.md files or to this README.md file. 


Test configuration is defined in the `tox.ini` file and includes
`py.test` tests and `flake8` source code checker.

You can run all of the tests:

```sh
misc/run_bash.sh
python setup.py test
```

or 

```sh
misc/run_tests_setup.sh
```


To run just the `py.test` tests, not `flake8`, and to re-use pipenv `virtualenv` do the following:

```sh
misc/run_bash.sh
py.test
```

or with 

```sh
misc/run_tests_pytest.sh
```


## Usage

```python
from pmc.restapi_client import RestApi

options = {
    'ENDPOINT': 'http://api.domain.tld/api',
    'LOGIN_PATH': 'auth/login/', # relative or absolute path to ENDPOINT
    'LOGOUT_PATH': 'auth/logout/', # relative or absolute path to ENDPOINT
}

new_item = {"field1": "value1", "field2": "value2"}
replace_item = {"field1": "value1_", "field2": "value2_"}
patch_item = {"field1": "value1_"}
email = "abc@domain.com"
passwd = "xyz"

api = RestApi(options)
ok = api.login(email=email, password=passwd)

if ok:
    x_list = api.resourceX.get()  # get a list of resourceX items
    x_item1 = api.resourceX(id).get()  # get an item of resourceX with id=id
    x_item2 = api.resourceX.post(new_item)  # post/create an item of resourceX
    api.resourceX(id).put(replace_item)  # put/replace an item of resourceX with id=id
    api.resourceX(id).patch(patch_item)  # patch/update partially an item of resourceX with id=id
    api.resourceX(id).delete()  # delete an item of resourceX with id=id
    api.resourceX.delete()  # delete all items of resourceX, potentially dangerous

```

## API