# Boston’s CityScore Toolkit

CityScore has transformed the way the City of Boston does performance management by delivering daily scores for key performance metrics to the Mayor and top city managers, allowing them to check in on the health of the City every day.

This CityScore toolkit is designed to allow your organization to use its own data to create and score a set of performance metrics. Using your data, the City of Boston's open-source CityScore algorithm will compile your daily performance on these metrics into a single number that grades your performance. 

Now, no matter your level of technological skill or infrastructure, the same performance tool is available to you. We’ve designed this toolkit to accepted data in three ways: 1) manual data entry; 2) uploading a .csv file; and 3) connecting directly to a SQL server. If you have a limited technical background or infrastructure, this tool can still be for you, just be sure to read the accompanying documentation thoroughly. 

You can access the toolkit in two ways. The first is a fully packaged Docker container, which is essentially a complete application that can run once downloaded on your machine. The second involves running it from source, for more technically-inclined users or those who want to modify the toolkit.

*For more detailed developer documentation, please refer to the [CityScore technical documentation](https://docs.google.com/document/d/1DSqCxMvQBMcE0YVHX-wk2B0iVos3TG8Fp7jSiD5JkLk/edit?ts=57b22cac).*

## Instructions for running Docker container (out-of-the-box solution recommended for less-technical users)
To access the fully packaged version, please follow these steps:

1. Create a free account on the [Docker Hub service](https://hub.docker.com).
2. Install the free version of Docker from [their website](https://www.docker.com/products/overview) that is compatible with your computer: either Docker for Windows / Docker for Mac or Docker Toolbox. 
3. Access a terminal as follows: 
    1. If you installed Docker for Windows / Docker for Mac, access your Windows command prompt or Mac OS terminal (if you’ve never used this, you can look up the name in your Start menu or Finder). 
	2. If you installed Docker Toolbox because your computer was not compatible with Docker for Windows / Docker for Mac, start Docker Quickstart Terminal instead. When the terminal starts, you should see a line near the top that looks like `docker is configured to use the default machine with IP 192.168.99.100`. Record the IP address at the end of the line (here, 192.168.99.100).
4. In this terminal, type in the statement: `docker run -p 8000:8000 cityofboston/cityscoretoolkit` and press Enter.
5. After the download completes, you should see a statement that resembles: 
```
Django version 1.9.7, using settings 'cityscorewebapp.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```
6. Copy and paste the address (here, http://0.0.0.0:8000/) into the browser of your choice to access the web toolkit. For those using Docker Toolbox, replace 0.0.0.0 with the IP you recorded above—in the example, http://192.168.99.100:8000/ to access the toolkit.
7. When you’re ready to close the toolkit, go ahead and enter `Ctrl+C` in the terminal. Then, type `docker ps` and hit Enter. You should see a row in a table where IMAGE is `cityofboston/cityscoretoolkit`; note the `CONTAINER ID` associated with that row, e.g. `724ed64c2ff7`. Then, enter `docker stop 724`, replacing 724 with the first few characters of the ID you recorded above. When you want to restart the toolkit, you can enter the command `docker start 724` to resume where you left off.

For a more detailed set of instructions for working with Docker, you can access https://github.com/wsargent/docker-cheat-sheet.


## Instructions for running app from source (recommended for technical users interested in app customization)
This application was written in the Django programming framework using the Python language. It uses Twitter's Bootstrap framework for visuals (CSS and JS), and HTML5 for the organization of its pages. The package also includes a Procfile and Dockerfile in case you wish to package the file and incorporate it into a larger platform. For more detailed developer documentation, please refer to the [CityScore technical documentation](https://docs.google.com/document/d/1DSqCxMvQBMcE0YVHX-wk2B0iVos3TG8Fp7jSiD5JkLk/edit?ts=57b22cac).

### Dependencies
- Python 2.7
- pip

### Installation

1. Download the package from GitHub by clicking on the green button that says “clone or download” and then selecting the "Download ZIP" option. This will create a local version of the application. From there, you will be able to start this application in a few easy steps. 
2. Once you’ve downloaded the package from GitHub, unzip the downloaded file into a directory of your choosing. That directory will become the path for the next step. Record or memorize the full path of the folder where you unzipped the package. For example, the path will likely look like: “C:/Users/username/downloads/cityscorewebapp-master”.
3. You can change the location of the package in your filesystem as much as you desire, but we recommend not changing the package structure. Once you've found the path, follow the appropriate steps for your OS:

#### Windows
1. Open the command prompt on your computer (if you do not know how to do this, you can search for “command prompt” after clicking your “Start” button.
2. Type in `cd /D C:/Downloads/cityscorewebapp-master` where the last part of that statement is the path you discovered above.
5. Then, type in `pip install -r requirements.txt` and wait for dependencies to install.
6. Once this finishes, type `python manage.py makemigrations`. You will see the following text in black and bold: 0014_auto_20160720_1254.py:
7. Now type `python manage.py migrate`. If you see a warning about URLs, you need not worry.
8. Finally, type in `python manage.py runserver`. You will see a paragraph like so: 
```
System check identified 1 issue (0 silenced). July 20, 2016 - 12:56:36 Django version 1.9.7, using settings 'cityscorewebapp.settings' Starting development server at http://127.0.0.1:8000/ Quit the server with CONTROL-C. To access your now-functional webapp, simply go to the address of the "development server" your project lists (in this case, http://127.0.0.1:8000/). 
```
9. You can now use your local computer as a server for the CityScore web application. This means you are now able to run the application self-sufficiently and all data is exclusively on this computer. Your data IS NOT collected from this package and you can use the webapp as though it were private to the computer you currently use. If you wish to share the webapp and make it run like a website, you will need to buy and configure a web server, which is outside the scope of this introduction.

#### Mac/OS

1. Open the terminal application on your computer
2. You should see a $ sign after your username in the terminal. Type in `cd /Users/username/Downloads/cityscore` where the last part of that statement is the path you discovered above.
3. Then, type in `pip install -r requirements.txt` and wait for dependencies to install.
4. Then, type `python manage.py makemigrations`. You will see the following text in black and bold: 0014_auto_20160720_1254.py:
5. Now type `python manage.py migrate`. If you see a warning about URLs, you need not worry.
6. Finally, type in `python manage.py runserver`. You will see a paragraph like so: 
```
System check identified 1 issue (0 silenced). July 20, 2016 - 12:56:36 Django version 1.9.7, using settings 'cityscorewebapp.settings' Starting development server at http://127.0.0.1:8000/ Quit the server with CONTROL-C. To access your now-functional webapp, simply go to the address of the "development server" your project lists (in this case, http://127.0.0.1:8000/). 
```
7. You can now use your local computer as a server for the CityScore web application. This means you are now able to run the application self-sufficiently and all data is exclusively on this computer. Your data IS NOT collected from this package and you can use the webapp as though it were private to the computer you currently use. If you wish to share the webapp and make it run like a website, you will need to buy and configure a web server, which is outside the scope of this introduction.

## About the CityScore toolkit
CityScore will prompt you to create a log-in. This log-in allows the City of Boston to notify users of updates to the project and collect statistics on usage. Closing the webapp tab will automatically log you out. Attempting to manually log out will cause the application to lose any cookies it has collected while you were logged in as it is native to your machine.

## Contributing
Fork it!
Create your feature branch: `git checkout -b my-new-feature`
Commit your changes: `git commit -am 'Add some feature'`
Push to the branch: `git push origin my-new-feature`
Submit a pull request :D Feel free to send us feature requests or your ideas for improving the toolkit at performance@boston.gov

## License
CDDL-1.0

