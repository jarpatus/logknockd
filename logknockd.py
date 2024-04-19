import logging
import os
import re
import subprocess
from pyconfigparser import configparser
from time import sleep
from watchfiles import watch

buffers = {}

def tail(conf):
  logger.info('Tailing {}...'.format(conf.file))
  file = open(conf.file, 'r')
  file.seek(0, os.SEEK_END)
  for changes in watch(conf.file):
    while row := file.readline():
      checkRuleset(conf, row.strip())

def checkRuleset(conf, row):
  logger.debug('Check row against ruleset: {}'.format(row))
  for rule in conf.ruleset:
    match = re.search(rule.filter, row);
    if match != None:
      key = rule.name+'.'+match.groups()[0]
      logger.debug('Row passed filter for rule {}, key: {}'.format(rule.name, key))
      if key not in buffers: buffers[key] = []
      buffer = buffers[key]
      buffer.append(row)
      while len(buffer) > len(rule.sequence):
        buffer.pop(0)
      if len(buffer) == len(rule.sequence):
        checkBuffer(rule, buffer)

def checkBuffer(rule, buffer):
  logger.debug('Checking rule {} buffer: {}'.format(rule.name, buffer))
  for i in range(len(rule.sequence)):
    match = re.search(rule.sequence[i], buffer[i])
    if match == None: return
    logger.debug('Rule {} sequence {} match.'.format(rule.name, i))
  runCommands(rule, match)

def runCommands(rule, match):
  logger.info('Rule {} buffer matched sequence, running commands...'.format(rule.name))
  for cmd in rule.cmds:
    run = cmd.format(*match.groups())
    logger.info(run)
    subprocess.run(run.split())

conf = configparser.get_config(config_dir='.', file_name='logknockd.yaml')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

while True:
  try:
    tail(conf)
  except Exception as e:
    logger.error(e)
  sleep(10)
