# PyVideo Lektor

Review and edit PyVideo.org data with a local copy in a lektor web instance

## Work in progress

Functionalities:

* Conversion:
  * [x] Convert pyvideo data to lektor format
  * [ ] Convert lektor format to pyvideo data
* Editor:
  * [ ] Edit events
  * [ ] Edit videos
  * [ ] Navigate between events in view mode
  * [ ] Navigate between videos in view mode
  * [ ] Navigate between events and videos in view mode


## Usage

Clone this repository and [pyvideo data](https://github.com/pyvideo/data) repository to (as example) `~/git`.

Convert pyvideo data to lektor
~~~ bash
# Installing lektor. See: https://www.getlektor.com/
curl -sf https://www.getlektor.com/install.sh | sh

# Cloning the repos
MY_GITHUB_USER=Daniel-at-github
cd ~/git/
git clone git@github.com:$MY_GITHUB_USER/pyvideo_lektor.git
git clone git@github.com:$MY_GITHUB_USER/data.git pyvideo_data # More clear name in local, renamed as pyvideo_data

# Converting pyvideo_data to lektor
#   only two events as example.
cd ~/git/pyvideo_lektor/bin
pipenv shell
./pyvideo_convert.py ~/git/pyvideo_data ~/git/pyvideo_lektor/ --events pyday-galicia-2017,pycon-us-2018 -v --pyvideo_to_lektor
~~~
