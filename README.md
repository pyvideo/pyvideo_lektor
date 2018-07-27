# PyVideo Lektor

Review and edit PyVideo.org data with a local copy in a lektor web instance

## Introduction

Adding conferences to [PyVideo data](https://github.com/pyvideo/data) is a process rather painful. Data gathering is already covered in PyVideo tools, but data reviewing is what PyVideo Lektor is intended to ease.  
With PyVideo Lektor you can:
* Convert this new data to a Lektor project.
* Then use Lektor to review the data builtin editor to:
  * Review the data.
  * Correct the data using Lektor built-in editor.
* Convert the reviewed data back to PyVideo data format.

## Work status

Beta. Seems to work OK. Interface is spartan.

Functionalities:

* Conversion:
  * [x] Convert pyvideo data to lektor format
  * [x] Convert lektor format to pyvideo data
* Editor (lektor local web):
  * [x] Navigate from events to videos in edit and view mode
  * [x] List of events and videos in view mode
  * [x] Edit events and videos


## Usage

Fork this repository and [pyvideo data](https://github.com/pyvideo/data) repository to (as example) `~/git`.

Convert pyvideo data to lektor
~~~ bash
# Installing lektor. See: https://www.getlektor.com/
curl -sf https://www.getlektor.com/install.sh | sh

# Cloning the repos (Use yours here if you forked it).
MY_GITHUB_USER=Daniel-at-github
cd ~/git/
git clone "git@github.com:$MY_GITHUB_USER/pyvideo_lektor.git"
git clone "git@github.com:$MY_GITHUB_USER/data.git" pyvideo_data # More clear name in local, renamed as pyvideo_data

# Converting pyvideo_data to lektor
#   only two events as example.
cd ~/git/pyvideo_lektor/bin
pipenv shell
./pyvideo_convert.py ~/git/pyvideo_data ~/git/pyvideo_lektor/review_web/ --events pyday-galicia-2017,pycon-us-2018 -v --pyvideo_to_lektor
~~~

Edit PyVideo data with lektor
~~~ bash
cd ~/git/pyvideo_lektor/review_web/
lektor serve
# Open http://127.0.0.1:5000/ in a web browser
~~~
To navigate this web, while constructing, use the builtin editor: http://127.0.0.1:5000/admin/root:events/preview
To navigate between videos in view mode use the [acces keys](https://www.w3schools.com/tags/att_accesskey.asp) P (Previous) N (Next)

Convert lektor to pyvideo data (Work in progress)
~~~ bash
cd ~/git/pyvideo_lektor/bin
pipenv shell
./pyvideo_convert.py ~/git/pyvideo_data ~/git/pyvideo_lektor/review_web/ -v --lektor_to_pyvideo
# Optionally, clean pyvideo lektor formated data
rm -fr ~/git/pyvideo_lektor/review_web/content/events/!(*.lr)
~~~
