<snippet>
  <content><![CDATA[
# ${1:The CityScore Toolkit}
This toolkit will allow a city or other organization to create a set of metrics 
which measure its performance. Then, the City of Boston's open-source CityScore
algorithm will compile your daily performance on these metrics into a single 
number that grades you on your organizational or citywide performance. This 
application revolutionized Boston's approach to daily city services under the
direction of Mayor Martin J. Walsh. Now, no matter what level of technological
prowess your city or organization possesses, the same facilities are available
to you. Get started!
This application was written in the Django programming framework using the Python
language. It uses Twitter's Bootstrap framework for visuals (CSS and JS), and
HTML5 for the organization of its pages. The package also includes a Procfile and
Dockerfile in case you the user wish to package the file and incorporate it into 
a larger platform.
## Installation
Download the package from GitHub using the "Download ZIP" option so you can 
create a local version of this application. From there, you will be able to start
this application in a few easy steps. First, though, you need to figure out the 
path to this application, or where it is on your computer. For example, on a Mac
the path will likely look like "/Users/username/Downloads/cityscore". You can change
the location of the package in your filesystem as much as you desire, but we here
at the City of Boston recommend not changing the package structure. Once you've found the path,
follow the appropriate steps for your OS:
### Mac/OS
1. Open the terminal application on your computer
2. You should see a $ sign after your username in the terminal. Type in 
"cd /Users/username/Downloads/cityscore" where the last part of that statement
is the path you discovered above.
3. Now type in the following exactly as you see here: "source venv/bin/activate"
4. You will see (venv) at the beginning of the new line. Once this occurs, type
"python manage.py makemigrations". You will see the following text in black and bold:
0014_auto_20160720_1254.py:
5. Now type "python manage.py migrate". If you see a warning about URLs, you need not worry.
6. Finally, type in "python manage.py runserver". You will see a paragraph like so:
System check identified 1 issue (0 silenced).
July 20, 2016 - 12:56:36
Django version 1.9.7, using settings 'cityscorewebapp.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
To access your now-functional webapp, simply go to the address of the 
"development server" your project lists (in this case, http://127.0.0.1:8000/).
You can now use your local computer as a server for the CityScore web application.
This means you are now able to run the application self-sufficiently and all data is
exclusively on this computer. Your data IS NOT collected from this package and you 
can use the webapp as though it were private to the computer you currently use.
If you wish to share the webapp and make it run like a website, you will need to
buy and configure a web server, which is outside the scope of this introduction.

## Usage
CityScore will allow you to create a log-in. This log-in is simply a layer of 
security and a way for us at City of Boston to know who uses the CityScore toolkit
so we can keep a potentially notify you of updates to the project. Once you are logged in,
the webapp has easy-to-access features and demonstrations of how to use its many features.
You do NOT need to log out of the application, simply close the tab in which it resides and the 
application will automatically log you out. Attempting to manually log out will cause the application
to lose any cookies it has collected while you were logged in as it is native to your machine.

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
Feel free to send us feature requests or your ideas for improving the toolkit at
cityscore@boston.gov

## Credits
Special thanks to Mayor Martin J. Walsh and his efforts to use data to create a 
strong and transparent vision of data-driven government. His initiative has
inspired this effort to bring the same to cities around the globe.
Additionally, thanks are due to the Department of Innovation and Technology at
the City of Boston for developing the algorithm behind the CityScore app.

## License
TODO: Write license

]]></content>
  <tabTrigger>readme</tabTrigger>
</snippet>