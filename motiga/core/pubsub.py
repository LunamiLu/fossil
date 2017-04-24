'''
Utility to keep separate entities decoupled while allowing them to inform
each other something has happened.
'''
from __future__ import print_function

import collections
import functools
import traceback

from pymel.core import warning, scriptJob


def getCallableAsStr(callable):
    '''
    Given a function or class, returns the string name to make unregistering after unloading work.
    '''
    return callable.__module__ + '.' + callable.__name__
    

class Event:
    '''
    All the available events.  Add new ones as needed.
    '''
    CARD_MIRROR_CHANGE = 0
    CARD_NAMEINFO_CHANGE = 1
    
    MAYA_DAG_OBJECT_CREATED = 2

    
# Preserve existing registered actions while allowing reloading the module
if '_registeredActions' not in globals():
    _registeredActions = collections.defaultdict( collections.OrderedDict )


def clear():
    global _registeredActions
    _registeredActions = collections.defaultdict( collections.OrderedDict )


def subscribe(event, action):
    '''
    When the given event is published, run the action.
    '''
    global _registeredActions
    if action not in _registeredActions[event]:
        _registeredActions[event][getCallableAsStr(action)] = action


def unsubscribe(event, action):
    '''
    Cease calling the action when the event is published.
    '''
    global _registeredActions
    try:
        del _registeredActions[event][getCallableAsStr(action)]
        #print( 'Unsubscribed', getCallableAsStr(action) )
    except KeyError:
        pass
        #print( 'Did not exist: unsubscribed', getCallableAsStr(action) )


def publish(event):
    '''
    Publish an event, which runs any associated actions.
    '''
    global _registeredActions
    
    for action in _registeredActions[event].values():
        # Catch errors
        try:
            action()
        except Exception:
            #print( traceback.format_exc() )
            warning('An error occurred in {0} when {1} was published'.format(action, event) )
            
            
#------------------------------------------------------------------------------
# Make dealing with some script jobs easier
#------------------------------------------------------------------------------

if 'selectionChangedId' not in globals():
    selectionChangedId = scriptJob(e=('DagObjectCreated', functools.partial(publish, Event.MAYA_DAG_OBJECT_CREATED)) )