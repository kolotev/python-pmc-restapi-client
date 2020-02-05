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
git clone ssh://git@bitbucket.be-md.ncbi.nlm.nih.gov:9418/pmc/python-pmc-restapi-client.git
cd python-pmc-restapi-client
misc/run_pipenv_init.sh 
misc/run_pip_install_req_dev.sh 
```

Then modify your requirements/*.in files, run 
```sh
misc/run_pip_multi.sh
misc/run_pip_install_req_dev.sh 
```
and now you are ready to start your development. 


### Notes:

- Do not forget to create new git tags
(to keep version of the package bumped/updated). 
- Do not forget to update CHANGELOG.md. 
- Do not forget to add descriptions to doc/*.md files or to this README.md file. 


Test configuration is defined in the `tox.ini` file and includes
`py.test` tests and `flake8` source code checker.

You can run all of the tests with one of the following command line snippets:

Run tests with pytest.
```sh
misc/run_tests_pytest.sh
```

Run tests with tox sequentially.
```sh
misc/run_tests_setup.sh
```

Run tox tests in parallel.
```sh
misc/run_tests_tox_p.sh
```

## Usage

```python
from pmc.restapi_client import RestApi, FtsClassFactory

# Details  on creating FtsClass classes.
#
# @max_tries - The maximum number of attempts to make before giving
# up. In the case of failure, the result of the last attempt
# will be returned. The value of None means there is no limit 
# to the number of tries.
#
# @max_time - The maximum total amount of time to try for before
# giving up. If this time expires, the result of the last
# attempt will be returned. 
#
# @max_value - The maximum value between tries.
 
# create a very Patient Fault Tolerant Type, which could be suitable
# for long running processes started from command line or crontab
PatientSessionType =  FtsClassFactory(max_tries=50, max_time=600, max_value=15)

# create a very Fast Fault Tolerant Type, which could be used
# in web services with low number of tries and with short
# tollerence period of falures.
ImpatientSessionType =  FtsClassFactory(max_time=3, max_value=1)

# By default the API is using the following limits for the session
# max_time = 300
# max_tries = None
# max_value = 30


end_point = 'http://api.domain/api'

# choose your scenarios of api client.
if environment == "Impatient":
    api = RestApi(ep=end_point, session=ImpatientSessionType)
elif environment == "Patient":
    api = RestApi(ep=end_point, session=PatientSessionType)
else:
    api = RestApi(ep=end_point)

new_item = {"field1": "value1", "field2": "value2"}
replace_item = {"field1": "value1_", "field2": "value2_"}
patch_item = {"field1": "value1_"}

root, response = api._.get()  # get root page of api (expected in json format)
xlist, response = api.resourceX.get()  # get a list of resourceX items
item1, response = api.resourceX(id).get()  # get an item of resourceX with id=id (id could be string or number)
item2, response = api.resourceX.post(json=new_item)  # post/create an item of resourceX
data, response = api.resourceX(id).put(json=replace_item)  # put/replace an item of resourceX with id=id
data, response = api.resourceX(id).patch(json=patch_item)  # patch/update partially an item of resourceX with id=id
data, response = api.resourceX(id).delete()  # delete an item of resourceX with id=id
data, response = api.resourceX.delete()  # delete all items of resourceX, potentially dangerous
data, response = api.resourceX.head() # get HEAD response for the list
data, response = api.resourceX(id).head() # get HEAD response for the item

# with all HTTP methods get(...), post(...), put(...), patch(...), delete(...), head(...)
# you may/should use arguments compatible with corresponding methods of widely used 
# requests or requests.Session python packages.
```

## API