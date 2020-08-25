# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os

import opentimelineio as otio

from .errors import MaglaError
from .data import MaglaData
from .entity import MaglaEntity
from .user import MaglaUser

from ..db.timeline import Timeline

try:
    basestring
except NameError:
    basestring = str

class MaglaTimelineError(MaglaError):
    """An error accured preventing MaglaTimeline to continue."""


class MaglaTimeline(MaglaEntity):
    """"""
    SCHEMA = Timeline

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaTimeline, self).__init__(self.SCHEMA, data or dict(kwargs))
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self.otio)

    @property
    def id(self):
        return self.data.id
    
    @property
    def label(self):
        return self.data.label
    
    @property
    def user(self):
        return self.data.user
    
    @property
    def otio(self):
        return self.data.otio
    
    @property
    def tree(self):
        return self.data.tree

    #### SQAlchemy relationship back-references
    @property
    def user(self):
        r = self.data.record.user
        if not r:
            return None
        return self.from_record(r)

    # MaglaTimeline-specific methods ______________________________________________________________
    def build(self, shots):
        for shot in shots:
            self.insert_shot(shot)
        
    def insert_shot(self, shot):
        # build tracks for given shot
        track_index = shot.track_index or 1
        if len(self.otio.tracks) < (track_index):
            for i in range(len(self.otio.tracks) - 1, track_index):
                self.otio.tracks.append(otio.schema.Track(name="background"))
        track = self.otio.tracks[track_index]
        t = list(track)
        # if there's no placement information place it at the end of current last clip.
        if not shot.start_time_in_parent:
            shot.data.start_time_in_parent = int(track.available_range().duration.value)
            shot.data.push()
        self.__insert_shot(track, shot)
            
    def __append_shot(self, track, shot):
        if len(track) > 0:
            gap_start = track.children[-1].range_in_parent().end_time_exclusive()
        else:
            gap_start = 0
            
        gap_duration = shot.start_time_in_parent - gap_start
        gap = otio.schema.Gap(duration=otio.opentime.RationalTime(gap_duration))
        track.extend([gap, shot.otio])
        return track
    
    def __insert_shot(self, track, shot):
        track_length = track.available_range().duration.value
        if track_length <= shot.start_time_in_parent:
            # easy just append a gap and our clip
            track = self.__append_shot(track, shot)
        else:
            # insert clip at it's `shot.start_time_in_parent` while splitting the `Gap`
            gap = track.child_at_time(shot.start_time_in_parent)
            if not isinstance(gap, otio.schema.Gap):
                raise MaglaTimelineError("Expected {0}, but got: {1}".format(type(gap), shot.otio))
            
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
            track.insert(track.index(gap) + 1, shot.otio)
            
            # append spacer gap if needed
            spacer_gap_duration = gap_duration - (new_gap_duration + shot.otio.source_range.duration)
            track.insert(track.index(gap) + 1, otio.schema.Gap(
                duration=otio.opentime.RationalTime(spacer_gap_duration, gap.duration.rate)))
            