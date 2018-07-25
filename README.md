# PyVideo Lektor

Review and edit PyVideo.org data with a local copy in a lektor web instance

## Work in progress

Functionalities:

* Conversion:
  * [x] Convert pyvideo data to lektor format
  * [x] Convert lektor format to pyvideo data
* Editor:
  * [x] Edit events
  * [x] Edit videos
  * [x] Navigate between events and videos in edit mode
  * [x] List of events in view mode
  * [x] Navigate between videos in view mode
  * [x] Navigate from events to videos in view mode
  * [ ] Fix dash titles bug
  * [ ] Enhance the web appearance. (Not mandatory)

## Usage

Fork this repository and [pyvideo data](https://github.com/pyvideo/data) repository to (as example) `~/git`.

Convert pyvideo data to lektor
~~~ bash
# Installing lektor. See: https://www.getlektor.com/
curl -sf https://www.getlektor.com/install.sh | sh

# Cloning the repos
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
