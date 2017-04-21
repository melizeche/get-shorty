# flask-get-shorty

A simple URL shortener capable of redirect to diferent targets according to the user device(desktop, mobile, tablet) written in Flask

## Requirements

* Python 3.5+
* Flask 0.12.1

## Installation

Virtualenv is optional but strongly suggested
```
git clone git@github.com:melizeche/get-shorty.git
cd get-shorty
virtualenv env -p python3.5
source env/bin/activate
pip install -r requirements.txt
```

## Usage
```
export FLASK_APP='getshorty.py'
flask initdb
flask run 0.0.0.0:5000
```
## API Docs
 see the [API.md](API.md) file for details
## Running the tests

```
python tests_shorty.py
```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## TODO

* Tests
* Proper documentation
* Use flask blueprints for api versioning


## Credits

* Marcelo Elizeche Landó

## License

This project is licensed under the terms of the MIT license - see the [LICENSE](LICENSE) file for details