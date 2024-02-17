# Stash-Aid

A work-in-progress webserver add-on to extend the functionality (and hopefully provide some QoL improvements) of your Stash media server.

## Installation Prerequisites

NodeJS

Python

Ensure you have NodeJS and Python installed on your system. You can download them from the following locations:

NodeJS: https://nodejs.org/

Python: https://www.python.org/downloads/

Setting up the Environment

Python Dependencies

The Python dependencies are listed in requirements.txt. To install these dependencies, run the following command in your terminal:

```pip install -r requirements.txt```

Node Dependencies

This project requires the following NodeJS packages: axios, puppeteer, and archiver. Install these packages using npm or yarn:

```npm install axios puppeteer archiver```

or

```yarn add axios puppeteer archiver```

## Usage

Running the Flask Server

The main server for stashAid can be launched via terminal from the directory containing 'stashAid.py'

```py stashAid.py```

From here, when you visit the server (server web address is in the terminal) you should be presented with a web page/admin panel with a few options:

![Main Page](.github/images/stashAid.png)


For more details on Python, visit the official documentation: https://docs.python.org/3/

For more details on NodeJS and npm packages, refer to the NodeJS documentation: https://nodejs.org/en/docs/ and the npm documentation: https://docs.npmjs.com/
