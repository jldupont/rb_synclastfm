README
======

This project consists of a Rhythmbox plugin which consists in "music collection synchronization features" with Last.fm.  

Features
========

1. Fill "rating" with "loved" field: when a track is locally unrated (i.e. not rating on Rhythmbox), the "loved" field of the track
is checked from the user's profile on Last.fm; if the track is "loved" then the track rating will be set to "5 stars". 

2. Download "play count": the count associated with a track is downloaded from Last.fm and the local "playcount" field is updated if the count retrieved from last.fm is greater than 0.

3. Interface to "lastfm-proxy-dbus" through DBus: provides "syncing" of 'playcount' of the user's tracks from the "Recent Tracks" journal on Last.fm.

4. Interface to "musicbrainz-proxy-dbus": provides resolving [artist;track] with Musicbrainz.

Musicbrainz
===========

[Musicbrainz](http://www.musicbrainz.org/) provides a Webservice API for resolving music tracks to unique identifiers. 
This service is flexible in mapping the said tracks in face of common errors. This facility increases the likelyhood
of finding a match between a track in Rhythmbox's library against a track "scrobble" over to Last.fm. 

Installation
============
There are 2 methods:

1. Use the Ubuntu Debian repository [jldupont](https://launchpad.net/~jldupont/+archive/jldupont)  with the package "rbsynclastfm"

2. Use the "Download Source" function of this git repo and place the "rbsynclastfm" folder in ".gnome/rhythmbox/plugins

Note that option #2 isn't preferred as one might get an "unstable" snapshot. 

Dependencies
============

The Last.fm plugin for Rhythmbox must be installed and configured (though not necessarily active). 
This requirement ensures that the "username" parameter for the current user's Last.fm profile can be found.

* (optional) [Musicbrainz-proxy-bus](http://github.com/jldupont/musicbrainz-proxy-dbus) : for increased [artist;track] resolving capabilities against the RB library.
* (optional) [Lasfm-proxy-dbus](http://github.com/jldupont/lastfm-proxy-dbus) : for pulling the user's recent tracks journal (API "user.recenttracks") from Last.fm.
