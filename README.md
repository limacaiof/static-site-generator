# Static Site Generator

A Python static site generator made from scratch. Turning Markdown into a well designed HTML project. Similar to Hugo, Gatsby and Jekyll.

This is a [Boot.dev](https://www.boot.dev) project.

## Technologies
 - **Python**


## Features
 - Easy to use and lightweight
 - High customizable templates
 - Convert any valid Markdown into HTML pages
 - Unit Tests

 ## How to run
 1. On the project directory, move your markdown files into the `/content` directory. Or simply use the default markdown files.
 2. In the terminal, start the server by the following command. This will convert all markdown files inside `/content` and serve all new HTML files in the port :8888
 ```bash
./main.sh
 ```
 3. To run the unit test, use the following command:
 ```bash
./test.sh
 ```

 ## Usage
 * Every change inside your template, you need to restart the server that will display all the new changes.
 * Pictures, CSS and Scripts can be added inside the `static/` directory
 * In case of permission issues when running `./main.sh` or `./test.sh`, add the executable permission to the following scripts by running:
 ```bash
 chmod +x main.sh test.sh
 ```
