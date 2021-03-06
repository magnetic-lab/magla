# -*- coding: utf-8 -*-
"""Timelines are trackless and clipless representations of an `opentimelineio.schema.Timeline`
    which self-build themselves dynamically based on whatever list of `MaglaShot` you feed in."""
import getpass
import logging
import os

import opentimelineio as otio
from opentimelineio.opentime import RationalTime as RTime

from ..db.timeline import Timeline
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaTimelineError(MaglaError):
    """An error accured preventing MaglaTimeline to continue."""


class MaglaTimeline(MaglaEntity):
    """Provide an interface for building and exporting `opentimelineio.schema.Timeline`.

    For usage see `magla.core.project.MaglaProject`
    """
    __schema__ = Timeline

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaTimeline, self).__init__(data or dict(kwargs))

    def __repr__(self):
        return "<Timeline {this.id}: name={this.otio.name}, label={this.label}, user={this.user}>".format(this=self)

    def __str__(self):
        return self.__repr__()

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
        return self

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
                self.otio.tracks.append(otio.schema.Track(name="magla_track_{index}".format(
                    index=i
                )))
        track = self.otio.tracks[track_index-1]
        shot.data.track_index = track_index
        # if there's no placement information place it at the end of current last clip.
        clip = track.child_at_time(
            RTime(shot.start_frame_in_parent or 0, shot.project.settings_2d.rate))
        if shot.start_frame_in_parent == None or clip:
            shot.data.start_frame_in_parent = int(
                track.available_range().duration.value)
        shot.data.push()
        self.__insert_shot(shot)

    def __append_shot(self, shot, gap=None):
        """Append an `opentimelineio.schema.Gap` if needed, then append given shot to it's track.

        Parameters
        ----------
        shot : magla.core.shot.MaglaShot
            The `MaglaShot` to append
        gap : opentimelineio.schema.Gap
            The gap to insert if provided
        """
        if gap:
            self.data.otio.tracks[shot.track_index-1].extend([gap, shot.otio])
        else:
            self.data.otio.tracks[shot.track_index-1].append(shot.otio)

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
        start_frame = float(shot.start_frame_in_parent)
        if start_frame == x:
            # no gap needed
            self.__append_shot(shot)
        elif start_frame > x:
            # gap needed
            last_clip = track[-1]
            gap_start = last_clip.range_in_parent().end_time_exclusive().value
            gap_duration = start_frame - gap_start
            gap = otio.schema.Gap(duration=RTime(float(gap_duration)))
            self.__append_shot(shot, gap)
        else:
            # insert clip at it's `start_frame` while splitting the `Gap`
            gap = track.child_at_time(RTime(
                start_frame, shot.project.settings_2d.rate))
            if not isinstance(gap, otio.schema.Gap):
                raise MaglaTimelineError(
                    "Expected {0}, but got: {1}".format(otio.schema.Gap, gap))

            # prepare to split gap for insertion
            gap_start = gap.range_in_parent().start_time
            gap_duration = gap.range_in_parent().end_time_exclusive() - gap_start

            # define new gap duration
            new_gap_duration = RTime(start_frame - gap_start, gap_duration.rate)

            # apply new gap duration
            gap.source_range = otio.opentime.TimeRange(
                start_time=gap_start,
                duration=new_gap_duration)

            # insert our shot clip
            self.otio.tracks[track_index-1].insert(track.index(gap) + 1, shot.otio)

            # append spacer gap if needed
            gap_duration = gap_duration - (new_gap_duration + shot.otio.source_range.duration)
            self.otio.tracks[track_index-1].insert(track.index(gap) + 1, otio.schema.Gap(
                duration=RTime(gap_duration, gap.duration.rate)))
