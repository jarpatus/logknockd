#!/usr/bin/python
import json
import os
import re
import subprocess
from time import sleep

buffers = {}

def debug(msg): print('[DEBUG]', msg)
def info(msg): print('[DEBUG]', msg)
def error(msg): print('[DEBUG]', msg)

def getConf():
  file = open('logknockd.conf', 'r')
  conf = json.load(file)
  file.close()
  return conf

def tail(noSeek=False):
  info('Tailing {}...'.format(conf['file']))
  while True:
    file = open(conf['file'], 'r')
    if not noSeek: file.seek(0, os.SEEK_END)
    noSeek = read(file)
    file.close()

def read(file):
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
  debug('Check row against ruleset: {}'.format(row))
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
  debug('Checking rule {} buffer: {}'.format(rule['name'], buffer))
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

while True:
  try:
    tail()
  except Exception as e:
    error(e)
  sleep(10)
