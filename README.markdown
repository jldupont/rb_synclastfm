README
======

This project consists of a Rhythmbox plugin which consists in "music collection synchronization features" with Last.fm.  

Features
========

1. Fill "rating" with "loved" field: when a track is locally unrated (i.e. not rating on Rhythmbox), the "loved" field of the track
is checked from the user's profile on Last.fm; if the track is "loved" then the track rating will be set to "5 stars". 

2. Download "play count": the count associated with a track is downloaded from Last.fm.

Installation
============
There are 2 methods:

1. Use the Ubuntu Debian repository [jldupont](https://launchpad.net/~jldupont/+archive/jldupont)  with the package "rbsynclastfm"

2. Use the "Download Source" function of this git repo and place the "rbsynclastfm" folder in ".gnome/rhythmbox/plugins
