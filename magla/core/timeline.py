# -*- coding: utf-8 -*-
"""Timelines are trackless and clipless representations of an `opentimelineio.schema.Timeline`
    which self-build themselves dynamically based on whatever list of `MaglaShot` you feed in."""
import getpass
import logging
import os

import opentimelineio as otio

from ..db.timeline import Timeline
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaTimelineError(MaglaError):
    """An error accured preventing MaglaTimeline to continue."""


class MaglaTimeline(MaglaEntity):
    """Provide an interface for building and exporting `opentimelineio.schema.Timeline`.
    
    For usage see `magla.core.project.MaglaProject`
    """
    SCHEMA = Timeline

    def __init__(self, data, *args, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaTimeline, self).__init__(self.SCHEMA, data or dict(kwargs))

    def __str__(self):
        """Overwrite the default string representation.

        Returns
        -------
        str
            Display the native `opentimelineio` representation
        """
        return str(self.otio)

    def __repr__(self):
        return self.__str__()

    @property
    def id(self):
        """Retrieve id from data.

        Returns
        -------
        int
            Postgres column id
        """
        return self.data.id

    @property
    def label(self):
        """Retrieve label from data.

        Returns
        -------
        str
            A descriptive label for the timeline
        """
        return self.data.label

    @property
    def otio(self):
        """Retrieve otio from data.

        Returns
        -------
        opentimelineio.schema.Timeline
            The live timeline object
        """
        return self.data.otio

    # SQAlchemy relationship back-references
    @property
    def user(self):
        """Shortcut method to retrieve related `MaglaUser` back-reference.

        Returns
        -------
        magla.core.user.MaglaUser
            The `MaglaUser` owner of this timeline if any
        """
        r = self.data.record.user
        if not r:
            return None
        return MaglaEntity.from_record(r)

    # MaglaTimeline-specific methods ______________________________________________________________
    def build(self, shots):
        """Build necessary tracks and populate with given shots.

        Parameters
        ----------
        shots : list
            List of shots to populate timeline with
        """
        shots = sorted(shots, key=lambda shot: shot.id)
        for shot in shots:
            self.insert_shot(shot)

    def insert_shot(self, shot):
        """Insert given shot into timeline.

        Parameters
        ----------
        shot : magla.core.shot.MaglaShot
            The `MaglaShot` to insert
        """
        # build tracks for given shot
        track_index = shot.track_index or 1
        num_tracks = len(self.otio.tracks)
        if num_tracks < (track_index):
            for i in range(num_tracks, track_index):
                self.otio.tracks.append(otio.schema.Track(name="background"))

        # if there's no placement information place it at the end of current last clip.
        if shot.start_time_in_parent == None:
            track = self.otio.tracks[track_index-1]
            shot.data.start_time_in_parent = int(
                track.available_range().duration.value)
            shot.data.push()
        self.__insert_shot(shot)

    def __append_shot(self, shot):
        """Append an `opentimelineio.schema.Gap` if needed, then append given shot to it's track.

        Parameters
        ----------
        shot : magla.core.shot.MaglaShot
            The `MaglaShot` to append
        """
        track_index = shot.track_index or 1
        if len(self.otio.tracks[track_index-1]) > 0:
            last_clip = self.otio.tracks[track_index-1][-1]
            gap_start = last_clip.range_in_parent().end_time_exclusive().value
            gap_duration = shot.start_time_in_parent - gap_start
            gap = otio.schema.Gap(
                duration=otio.opentime.RationalTime(gap_duration))
            self.otio.tracks[track_index-1].extend([gap, shot.otio])
        else:
            self.otio.tracks[track_index-1].append(shot.otio)

    def __insert_shot(self, shot):
        """Insert an `opentimelineio.schema.Clip` by splitting the occupying `Gap`.

        Parameters
        ----------
        shot : magla.core.shot.MaglaShot
            The `MaglaShot` to append

        Raises
        ------
        MaglaTimelineError
            Thrown if anything other than an `opentimelineio.schema.Gap` is encountered
        """
        track_index = shot.track_index or 1
        track = self.otio.tracks[track_index-1]
        x = track.available_range().duration.value
        if x <= shot.start_time_in_parent:
            # easy just append a gap + our clip
            self.__append_shot(shot)
        else:
            # insert clip at it's `shot.start_time_in_parent` while splitting the `Gap`
            gap = track.child_at_time(otio.opentime.RationalTime(
                shot.start_time_in_parent, shot.project.settings_2d.rate))
            if not isinstance(gap, otio.schema.Gap):
                raise MaglaTimelineError(
                    "Expected {0}, but got: {1}".format(type(gap), shot.otio))

            # prepare to split gap for insertion
            gap_start = gap.range_in_parent().start_time
            gap_duration = gap.range_in_parent().end_time_exclusive() - gap_start

            # define new gap duration
            new_gap_duration = otio.opentime.RationalTime(
                shot.start_time_in_parent - gap_start, gap_duration.rate)

            # apply new gap duration
            gap.source_range = otio.opentime.TimeRange(
                start_time=gap_start,
                duration=new_gap_duration)

            # insert our shot clip
            self.otio.tracks[track_index].insert(
                track.index(gap) + 1, shot.otio)

            # append spacer gap if needed
            spacer_gap_duration = gap_duration \
                - (new_gap_duration + shot.otio.source_range.duration)
            self.otio.tracks[track_index].insert(track.index(gap) + 1, otio.schema.Gap(
                duration=otio.opentime.RationalTime(spacer_gap_duration, gap.duration.rate)))
