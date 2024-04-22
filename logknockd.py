#!/usr/bin/python
import json
import os
import re
import subprocess
from time import sleep
from inotify_simple.inotify_simple import INotify, flags

def trace(msg): 
  if conf['trace']: print('[TRACE]', msg)

def debug(msg): 
  if conf['debug']: print('[DEBUG]', msg)

def info(msg): 
  print('[INFO]', msg)

def error(msg): 
  print('[ERROR]', msg)

def getConf():
  file = open(os.path.dirname(__file__)+'/logknockd.conf', 'r')
  conf = json.load(file)
  file.close()
  return conf

def tail(noSeek=False):
  info('logknockd tailing {}...'.format(conf['file']))
  while True:
    debug('Opening {}...'.format(conf['file']))
    file = open(conf['file'], 'r')
    if not noSeek: file.seek(0, os.SEEK_END)  
    noSeek = notify(file)
    file.close()
    sleep(3)

#
# Note that inotify cannot tell us if file was truncated, nor deleted (because we have open handles DELETE_SELF won't work).
# In typical log monitoring scenarios this does not happen though so let's blissfully ignore this and poll can be used instead 
# if truncates or deletes happens. It would also be possible to write hybrid function using os.stat() when flags.ATTRIB is 
# is detected but let's be hyper resource conservative as well with this function.
#
def notify(file):
  inotify = INotify()
  wd = inotify.add_watch(conf['file'], flags.MODIFY | flags.MOVE_SELF)
  while row := file.readline(): checkRuleset(row.strip())
  while True:
   for event in inotify.read():
    if event.mask & event.mask & flags.MOVE_SELF:
      debug('File moved or deleted, re-opening...')
      while row := file.readline(): checkRuleset(row.strip())
      inotify.rm_watch(wd)
      return True
    if event.mask & flags.MODIFY:
      trace('File modified, reading...')
      while row := file.readline(): checkRuleset(row.strip())

def poll(file): 
  stat = None
  while True:
    newstat = os.stat(conf['file'])
    if stat is not None and newstat.st_ino != stat.st_ino:
      debug('File re-created, reading and re-opening...')
      while row := file.readline(): checkRuleset(row.strip())
      return True
    if stat is not None and newstat.st_size < stat.st_size:
      debug('File truncated, seek to start...')
      file.seek(0)      
    if stat is None or newstat.st_mtime > stat.st_mtime:
      while row := file.readline(): checkRuleset(row.strip())
    stat = newstat
    sleep(3)
 
def checkRuleset(row): 
  trace('Check row against ruleset: {}'.format(row))
  for rule in conf['ruleset']:
    match = re.search(rule['filter'], row);
    if match != None:
      key = rule['name']+'.'+match.groups()[0]
      debug('Row passed filter for rule {}, key: {}'.format(rule['name'], key))
      if key not in buffers: buffers[key] = []
      buffer = buffers[key]
      buffer.append(row)
      while len(buffer) > len(rule['sequence']): 
        buffer.pop(0)
      if len(buffer) == len(rule['sequence']): 
        checkBuffer(rule, buffer)

def checkBuffer(rule, buffer):
  trace('Checking rule {} buffer: {}'.format(rule['name'], buffer))
  for i in range(len(rule['sequence'])): 
    match = re.search(rule['sequence'][i], buffer[i])
    if match == None: return 
    debug('Rule {} sequence {} match.'.format(rule['name'], i))
  runCommands(rule, match)

def runCommands(rule, match): 
  info('Rule {} buffer matched sequence, running commands...'.format(rule['name']))
  for cmd in rule['cmds']:
    run = cmd.format(*match.groups())
    info(run)
    subprocess.run(run.split())

conf = getConf();
buffers = {}

while True:
  try:
    tail()
  except Exception as e: 
    error('Exception: {}'.format(repr(e)))
  sleep(10)
